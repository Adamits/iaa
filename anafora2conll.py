"""
In order to use the reference corefscorer, we need coref data in the CoNLL-2011/2012 format

This script will convert an anafora XML to that format, and optionally generate extra
coref other than what is reported by IDENT chains, inferred via structure links for a
'loose' IAA score.

By: Adam Wiemerslage
09/05/2018
"""
import argparse
import codecs
from bs4 import BeautifulSoup as soup
from reference_coreference_scorers import averaged_scorer
from anafora4python import annotation

def infer_refs(ref_dict, ref_list, ref):
  """
  ref_dict: the adjacency table for the undirected cyclic graph we are traversing
  ref_list: the list of already traversed refs
  ref: the current ref being traversed

  Recursively traverse the adjacency list (implemented as a dict)
   and add everything in that traversal to a single output list.

  We are doing a DFS and considering cycles to be terminal nodes
  (basically do a DFS, and put everything we come across into a list, ignoring cycles.)
  """
  for inferred_ref in ref_dict.get(ref, []):
    if inferred_ref not in ref_list:
      ref_list.append(inferred_ref)
      for x in infer_refs(ref_dict, ref_list, inferred_ref):
        if x not in ref_list:
          ref_list.append(x)

  return ref_list

def merge_coref_rows(coref_matrix):
  """
  Traverse the rows of the coref matrix, look for entities that appear in multiple rows,
   and merge those rows, returning the matrix that results from those merge operations

  Return: list of lists of coreferring entity IDS.
  """
  output_matrix = []
  # For tracking which rows point to other rows, by a shared entity
  ref_dict = {}
  ######
  # In n^2 we build an adjacency matrix that has an edge
  # between the indices of rows that share an entity
  ######
  for i, row in enumerate(coref_matrix):
    ref_dict[i] = []
    for j, other_row in enumerate(coref_matrix):
      # A row cannot point to itself
      if i == j:
        continue
      if set(row).intersection(other_row):
        # Add index of row from coref matrix to be merged in ref_row
        ref_dict[i].append(j)

  # Now we have a ref_dict of all rows that point to each other.
  # This is an undirected cyclic graph.
  # Essentially, each row represents a merge operation that needs to happen.
  merged_ref_rows = []
  # For tracking the index of already merged rows to avoid redundancy
  merged_refs = []
  for i, row in ref_dict.items():
    #if i in merged_refs:
    #  continue
    inferred_refs = []
    # Need to get any further mergable rows by traversing the hash
    for ref in row:
      inferred_refs += infer_refs(ref_dict, [], ref)

    # We need a reference to current row (i), all directly coreferring rows, and all inferable rows
    # Via the directly coreferring rows.
    merged_ref_rows.append([i] + row + inferred_refs)
    #merged_refs += row
    #merged_refs += inferred_refs

  # Finally, loop over the matrix of row indices, and look them up in coref matrix,
  # and return the result.
  for i, ref_row in enumerate(merged_ref_rows):
    # Set the actual entitiy ID's from the refs
    output_matrix.append(list(set([e for ref in ref_row for e in coref_matrix[ref]])))

  return output_matrix

# TODO: partitions should only comprise IDENT chains of the setting type
# TODO: (either cross or within doc). But we need to infer via ALL relations.
# TODO: For strict metric, we should still infer via within doc rels.
def get_coref_matrix(idents, inference_rels):
  """
  Given relations, we get a matrix whose rows are a single coref chains.
   this considers structural links as coref as well and 'infers' more links,
   we then merge the coref chains who share at least a single entity.
   Finally, the 'inference' rels are removed leaving only partitions of the
   original IDENTs

  Return: list of lists of coreferring entity IDS.
  """
  ident_ids = [ident.entity_ids() for ident in idents]
  inference_ids = [inference_rel.entity_ids() for inference_rel in inference_rels]
  coref_matrix = ident_ids + inference_ids
  # Merge all of the rows that share a relation
  coref_matrix = merge_coref_rows(coref_matrix)
  # Remove the entities  from the matrix
  # PRETTY SURE WE DONT WANT TO DO THIS
  #for i, row in enumerate(coref_matrix):
  #  coref_matrix[i] = [c for c in row if c in ident_ids]

  return coref_matrix

def make_conll_file(input, output, mode="loose", setting="single-doc"):
  """
  Writes the .conll file of partitions from the data.

  Single-doc vs Cross-doc: This determines which IDENT links we are quantifying IAA for,
    in the cross-doc case, we only care about IDENT links that span >1 document.

  Loose vs. Strict mode: In loose mode we can infer more IDENT partitions via
   other relations. Whereas in strict mode, the partitions are not inferrable other than
   by any 'necessary' inference, e.g. in the cross-doc case, via within-doc relations.
  """
  fn = input.split("/")[-1]
  doc = annotation.Document(soup(open(input), "xml"), fn)
  if setting == "single-doc":
    inference_rels = doc.get_within_doc_contains_subevent_tlinks() + \
                     doc.get_within_doc_whole_parts() + \
                     doc.get_within_doc_set_subsets()
    matrix = get_coref_matrix(doc.get_within_doc_identical_chains(), inference_rels, mode)
  elif setting == "cross-doc":
    # We can infer via ANY structural/ident rel
    if mode == "loose":
      inference_rels = doc.get_contains_subevent_tlinks() \
                     + doc.get_whole_parts()\
                     + doc.get_set_subsets()\
                     + doc.get_within_doc_identical_chains()
    else:
      # In strict mode, we still want to infer via within-doc (just ident?) links
      inference_rels = []#doc.get_within_doc_identical_chains()

    matrix = get_coref_matrix(doc.get_cross_doc_identical_chains(), inference_rels)
  else:
    raise Exception("%s is not a valid setting, you can only use cross-doc, or single-doc" % setting)

  entityid2corefid = {}
  for coref_id, row in enumerate(matrix):
    for entity_id in row:
      entityid2corefid[entity_id] = coref_id
  with codecs.open(output, 'w') as out:
    docid = doc.filename.split('.')[0]
    out.write("#begin document (%s);\n" % docid)
    outlist = []

    for entity_id in doc.get_sorted_entity_ids():
      coref_id = str(entityid2corefid.get(entity_id, "-"))
      coref_id = "(" + coref_id + ")" if coref_id != "-" else coref_id
      outlist.append('\t'.join([docid, entity_id.split("@")[0], coref_id]))

    out.write('\n'.join(outlist))
    out.write("\n\n#end document")

if __name__=='__main__':
  parser = argparse.ArgumentParser(description="Convert an Anafora XML to conll format for coref scoring")
  parser.add_argument('--input', help="input file", required=True)
  parser.add_argument('--filetype', help="file type, e.g. THYME2v1-correction")
  parser.add_argument('--output', help="output file, ending in .conll")
  parser.add_argument('--infer_rels', help='Infer IDENT relations based on structural links', action='store_true')

  args = parser.parse_args()
  input = args.input
  file_type = args.filetype
  output = args.output
  infer = args.infer_rels

  make_conll_file(input, output)
