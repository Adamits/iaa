def _get_idents_with(idents, ent):
  """
  Return: a list of all entity ids that are in an ident chain
  with ent_id in document
  """
  if ent is not None:
    idents = [ident for ident in idents if ent.id in ident.entity_ids()]
    # Return a flat list of the ids of each entity the input is identical with
    # Note that hypothetically one mention should be for one entity,
    # so there should NOT be more than one ident chain. But due to annotator error, it happens.
    return [entity.id_doc_num for ident in idents for entity in ident.get_entities()]
  else:
    return []


def _infer_structural_rel(head, tail, idents):
  """
  Get the inferred CONS SUB rels for a given source and target.
  Return a tuple of ([source_ids], [target_ids]).

  This is because all ident sources should be in a CONS SUB
  with all ident targets, and we do not want to waste time
  permuting all combinations.
  """
  head_ids = [head.id_doc_num]
  tail_ids = [t.id_doc_num for t in tail]

  head_ids += _get_idents_with(idents, head)
  for t in tail:
    tail_ids += _get_idents_with(idents, t)

  return (head_ids, tail_ids)

def _agrees(x, y, identsy):
  """
  Compare two annotation objects for agreement.

  We only check inferable CONS-SUB in y, to conform to checking
  for each annotation, against the inferable relations from 'other' annotator

  This is only done in 'loose' mode
  """
  # If the two relations have the same source and target
  if x == y:
    return True
  # Check if they agree with inferred relations found via IDENT chains
  else:
    # Get inferred sources and targets
    head_idsy, tail_idsy = _infer_structural_rel(y.get_head(), y.get_tail(), identsy)

    # Check the intersection of both sets of inferred arguments, to infer agreement
    if x.get_head().id_doc_num in head_idsy and set([t.id_doc_num for t in x.get_tail()]).issubset(tail_idsy):
      return True
    else:
      if x.get_head().id == y.get_head().id and len(tail_idsy) < len(y.get_tail()):
        print("Disagree!")
        print("%s disagrees with %s" % (x.id, y.id))
        h = x.get_head()
        t = x.get_tail()[0]
        h2 = y.get_head()
        t2 = y.get_tail()[0]
        print("Head %s at span %s and Tail %s at span %s" % (h.id, h.span_string, t.id, t.span_string))
        print("Head %s at span %s and Tail %s at span %s" % (h2.id, h2.span_string, t2.id, t2.span_string))

      return False

def _has_agreement_in(rel_from, rels_to, idents_to):
  """
  Check if rel_from in doc_from has an
  agreeing relation in doc_to

  rel_from: The structural relation anafora4python object (e.g. CON-SUB, W-P, S-SS)
    for which we are looking for a match
  rels_to: The structural relation anafora4python object
    that we are testing as a potential match
  idents_to: The list of IDENT relation anafora4python objects
    from which we can infer more relations
  mode: "loose" or "strict". Loose means that we can infer the relations of rels_to via the idents_to

  return: Boolean as to whether or not there is a (potentially inferable) agreement
  """
  for rel_to in rels_to:
    if rel_to.has_empty_args():
      continue
    if _agrees(rel_from, rel_to, idents_to):
      return True

  print("%s HAS NO AGREEMENT!!!" % rel_from.id)
  return False

def get_crossdoc_agreement(rels1, rels2, idents1, idents2):
  """
  Compute the agreement between two sets of crossdoc relations, of the same relation type

  Return: (scalar IAA score, total rel count doc1, total rel count doc2)
  """
  agreements = 0
  total_doc1 = 0
  total_doc2 = 0
  cross_rels1 = [r for r in rels1 if r.is_cross_doc()]
  cross_rels2 = [r for r in rels2 if r.is_cross_doc()]

  for cross_rel1 in cross_rels1:
    # IGNORE INCOMPLETE ANNOTATIONS
    if cross_rel1.has_empty_args():
      continue

    # Note we are comparing the cross_doc con-sub with ALL
    # con-sub in other doc. Thi includes single doc (gold) CON-SUB
    # Because these can be inferred as cross-doc via a cross-doc IDENT link.
    if _has_agreement_in(cross_rel1, rels2, idents2):
      agreements += 1

    total_doc1 += 1

  for cross_rel2 in cross_rels2:
    # IGNORE INCOMPLETE ANNOTATIONS
    if cross_rel2.has_empty_args():
      continue

    if _has_agreement_in(cross_rel2, rels1, idents1):
      agreements += 1
    #else:
    # print(cross_rel2.id)

    total_doc2 += 1

  total = total_doc1 + total_doc2
  if total == 0:
    return (None, None, None)
  else:
    return (agreements / total, total_doc1, total_doc2)

def get_crossdoc_agreement_by_structural_reltypes(doc1, doc2, mode="loose", reltypes=[]):
  """
  Computes the ITA between 2 documents for all
  relations of a certain type(s).

  doc1: A crossdoc document object from anafora4python
  doc1: A crossdoc document object from anafora4python to compare with
  mode: "loose" or "strict", loose means that we can infer relations in the to_doc via the ident relations
  reltypes: a list of the structural relation types that you want IAA from

  return: A dict of {'reltype': (IAA %, doc1 rel count, doc2 rel count), ...}
  """
  idents1 = doc1.get_identical_chains()
  idents2 = doc2.get_identical_chains()
  if mode == "strict":
    # In strict mode, we can only infer via within-doc IDENT
    idents1 = [ident for ident in idents1 if not ident.is_cross_doc()]
    idents2 = [ident for ident in idents1 if not ident.is_cross_doc()]
  iaa_dict = dict.fromkeys(reltypes)
  if "contains-subevent" in reltypes:
    con_subs1 = doc1.get_cross_doc_contains_subevent_tlinks()
    con_subs2 = doc2.get_cross_doc_contains_subevent_tlinks()

    iaa_dict["contains-subevent"] = get_crossdoc_agreement(con_subs1, con_subs2, idents1, idents2)
  if "whole-part" in reltypes:
    wp1 = doc1.get_cross_doc_whole_parts()
    wp2 = doc2.get_cross_doc_whole_parts()

    iaa_dict["whole-part"] = get_crossdoc_agreement(wp1, wp2, idents1, idents2)
  if "set-subset" in reltypes:
    s_ss1 = doc1.get_cross_doc_set_subsets()
    s_ss2 = doc2.get_cross_doc_set_subsets()

    iaa_dict["set-subset"] = get_crossdoc_agreement(s_ss1, s_ss2, idents1, idents2)

  return iaa_dict
