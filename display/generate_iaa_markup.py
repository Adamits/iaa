from iaa.relations import get_relation_agreement_by_type
from iaa.util import *

# For adding BootstrapCSS
def bootstrapHeader():
  # Add bootstrap css
  css_ref = "<link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css\">"
  # Add bootstrap JS
  js_ref = "<script src=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js\"></script>"

  return css_ref + js_ref

def generateIaaTable(agreement_dict, documents=[]):
  # percentage of total agreement over entities
  total = sum([(float(v['agree']) / float(v['total'])) for k, v in agreement_dict.items()]) / float(len(agreement_dict.keys()))
  if documents:
    result = '<h5 style="padding-bottom: 15px">%s vs %s  -  Total Agreement: %.2f%%</h5>' % (documents[0].annotator(), documents[1].annotator(), total * 100)
  else:
    result = ""
  result += '<table class="stripe hover row-border notetable" cellspacing="0" ><thead><tr>'
  result += '<th>Entity Type</th>'
  result += '<th>IAA</th>'
  result += '<th>IAA %</th>'
  result += '</tr></thead><tbody>'
  for type, agreement in agreement_dict.items():
    result += '<tr>'
    result += '<td>%s</td><td>%d/%d</td><td>%.2f</td>' % (
      type, agreement['agree'], agreement['total'], (float(agreement['agree']) / float(agreement['total'])) * 100)
    result += '</tr>'
  result += '</tbody></table>'

  return result

def modalAjax():
  result = '<script type="text/javascript">'
  result += 'jQuery(function($){'
  result += '$("body").on("click", "a.js-ita-modal", function(ev){'
  result += 'ev.preventDefault();'
  result += 'var modalTitle = $(this).data("modal-title");'
  result += '$("#iaaModal").find(".modal-content").find(".modal-title").html(modalTitle);'
  result += 'var uid = $(this).data("modal-file");'
  result += '$.get("thyme-iaa-modals/" + uid + ".html", function(html){'
  result += '$("#iaaModal").find(".modal-content").find(".modal-body").html(html);'
  result += '$("#iaaModal").modal("show", {backdrop: "static"});'
  # apply jQueryUI datatable code to newly rendered HTML
  result += '$(".notetable").DataTable();'
  result += '});'
  result += '});'
  result += '});'
  result += '</script>'

  return result

def generateIaaModal():
  result = '<div class="modal fade" id="iaaModal"><div class="modal-dialog" role="document">'
  result += '<div class="modal-content"><div class="modal-header">'
  result += '<h5 class="modal-title" style="display: inline-block;"></h5>'
  result += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">'
  result += '<span aria-hidden="true">&times;</span>'
  result += '</button></div>'
  result += '<div class="modal-body"></div>'
  result += '</div></div></div>'

  return result

def generateIaaCorpusBreakdown(schema, corpus, agreement_dict):
  # output_directory/iaa/schema/corpus/breakdown.html
  outdirstring = "%siaa/%s/%s/" % (output_directory, schema, corpus)
  try:
    outfile = open(outdirstring + "breakdown.html", 'w')
  except:
    os.makedirs(outdirstring)
    outfile = open(outdirstring + "breakdown.html", 'w')

  outfile.write(header())
  outfile.write('<div class="container">')
  outfile.write('<div style="margin: 20px 0px;"><a href="%s"><< Go Back</a></div>' % ROOT)
  outfile.write(generateIaaTable(agreement_dict))
  outfile.write('</div>')

def generateIaaModalContentFile(modal_id, documents, agreement_dict):
  '''
  Writes modal contents to /thyme-iaa-modals to be loaded with ajax
  '''
  out = open("%sthyme-iaa-modals/iaaModal_%s.html" % (output_directory, modal_id), 'w')
  out.write(generateIaaTable(agreement_dict, documents))
