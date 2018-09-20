from anafora4python.annotation import ContainsSubevent, Entity

def get_relation_agreement_by_type(doc1, doc2, type, mode="loose", setting="single-doc"):
  idents1 = doc1.get_identical_chains()
  idents2 = doc2.get_identical_chains()
  con_subs1 = doc1.get_contains_subevent_tlinks()
  con_subs2 = doc2.get_contains_subevent_tlinks()
  if type.lower() == "contains-subevent":
    if setting == "single-doc":
      return get_con_sub_agreement(con_subs1, con_subs2, idents1, idents2, mode=mode)
    elif setting == "cross-doc":
      import os, sys
      this_dir = os.path.dirname(os.path.realpath(__file__))
      sys.path.append(this_dir)
      from crossdoc.calculations import get_crossdoc_con_sub_agreement
      return get_crossdoc_con_sub_agreement(doc1, doc2, mode=mode)
  else:
    raise "ITA is not implemented for %s" % type

def get_idents_with(idents, ent):
  """
  Return: a list of all entity ids that are in an ident chain
  with ent_id in document
  """
  if ent is not None:
    idents = [ident for ident in idents if ent.id in ident.entity_ids()]
    # Return a flat list of the ids of each entity the input is identical with
    # Note that hypothetically one mention should be for one entity,
    # so there should NOT be more than one ident chain. But due to annotator error, it happens.
    return [entity.id_num for ident in idents for entity in ident.get_entities()]
  else:
    return []

def infer_con_sub(source, target, idents):
  """
  Get the inferred CONS SUB rels for a given source and target.
  Return a tuple of ([source_ids], [target_ids]).

  This is because all ident sources should be in a CONS SUB
  with all ident targets, and we do not want to waste time
  permuting all combinations.
  """
  source_ids = [source.id_num]
  target_ids = [target.id_num]

  source_ids += get_idents_with(idents, source)
  target_ids += get_idents_with(idents, target)

  return (source_ids, target_ids)

def agrees(x, y, identsy, mode):
  """
  Compare two annotation objects for agreement.

  We only check inferable CONS-SUB in y, to conform to checking
  for each annotation, against the inferable relations fro 'other' annotator
  """
  if mode not in ["loose", "strict"]:
    raise Exception("Must set a mode to either loose or strict!")
  # If the two CONS SUBS have the same source and target
  elif x == y:
    return True
  # Check if they agree with inferred relations found via IDENT chains
  elif mode == "loose":
    # Get inferred sources and targets
    source_idsy, target_idsy = infer_con_sub(y.get_source(), y.get_target(), identsy)

    # Check the intersection of both sets of inferred arguments, to infer agreement
    if x.get_source().id_num in source_idsy and x.get_target().id_num in target_idsy:
      return True
    else:
      return False
  else:
    return False

def has_agreement_in(con_sub_from, con_subs_to, idents_to, mode):
  """
  Check if con_sub_from in doc_from has an
  agreeing CONS-SUB relation in doc_to

  con_sub_from: The con-sub relation anafora4python object
    for which we are looking for a match
  con_subs_to: The con-sub relation anafora4python object
    that we are testing as a potential match
  idents_to: The list of IDENT relation anafora4python objects
    from which we can infer more con-sub relations

  return: Boolean as to whether or not there is an inferable agreement
  """
  for con_sub_to in con_subs_to:
    if con_sub_to.has_empty_args():
      continue
    elif agrees(con_sub_from, con_sub_to, idents_to, mode):
      return True

  return False

def get_con_sub_agreement(con_subs1, con_subs2, idents1, idents2, mode):
  """
  Computes the ITA between 2 documents for all
  contains-subevent relations.

  con_subs1: All contains-subevent links from doc1
  con_subs2: All contains-subevent links from doc2
  idents1: All identical links from doc1
  idents2: All identical links from doc2

  return: A scalar ITA score
  """
  agreements = 0
  total_doc1 = 0
  total_doc2 = 0

  for con_sub1 in con_subs1:
    # IGNORE INCOMPLETE ANNOTATIONS
    if con_sub1.has_empty_args():
      continue

    if has_agreement_in(con_sub1, con_subs2, idents2, mode=mode):
      agreements += 1

    total_doc1 += 1

  for con_sub2 in con_subs2:
    # IGNORE INCOMPLETE ANNOTATIONS
    if con_sub2.has_empty_args():
      continue

    if has_agreement_in(con_sub2, con_subs1, idents1, mode=mode):
      agreements += 1

    total_doc2 += 1

  total = total_doc1 + total_doc2
  if total == 0:
    return (None, None, None)
  else:
    return (agreements / total, total_doc1, total_doc2)
