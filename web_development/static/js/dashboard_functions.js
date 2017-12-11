function load_table(){
  html = "<center><img src='/static/images/loading.gif' style = 'width: 50px; margin: 0 auto; margin: 100px;'> </img></center>"
  $('#calendar').html(html);
  $.getJSON($SCRIPT_ROOT + '/calendar_json', {
    orgcode: $('#orgcode').val(),
    modality: $('#modality').val(),
    departmentcode: $('#departmentcode').val()
  }, function(data) {
    columns_names = data.result.columns_names;
    row_names = data.result.row_names;
    rows = data.result.rows;

    var html = "";
    html+='<table class="table table-bordered"><thead>';
    for (var i=0;i<columns_names.length;i++){
      html+= "<th>" + columns_names[i] + "</th>";
    }
    html+='</thead><tbody>';
    for (var i=0;i<rows.length;i++){
      html+= '<tr>';
      var row_name = row_names[i];
      html+= "<td>" + row_name + "</td>";

      var columns = rows[i];
      for (var j=0;j<columns.length;j++){
        var time_slot = columns[j];
        if (time_slot.status == 0){
          html+= "<td class='time_slot bg-grey' data-toggle='tooltip' data-container='body'"
          html+= "data-exam-id='"+time_slot.exam_id+"'"
          html+= "data-patient-id='"+time_slot.patient_id+"'"
          html+= "data-age='"+time_slot.age+"'"
          html+= "data-gender='"+time_slot.gender+"'"
          html+= "title = 'Cancel Probablity: "+time_slot.probability+"'></td>";
        } else if (time_slot.status == 1) {
          html+= "<td class='time_slot bg-blue' data-toggle='tooltip' data-container='body'"
          html+= "data-exam-id='"+time_slot.exam_id+"'"
          html+= "data-patient-id='"+time_slot.patient_id+"'"
          html+= "data-age='"+time_slot.age+"'"
          html+= "data-gender='"+time_slot.gender+"'"
          html+= "title = 'Cancel Probablity: "+time_slot.probability+"'></td>";
        } else {
          html+= "<td class='time_slot'></td>";
        }
      }
    html+= '</tr>';
    }
    html+='</tbody></table>';

    $('#calendar').html(html);
    $('[data-toggle="tooltip"]').tooltip();



  });
}

function load_modalities(modalities){
  var $el = $("#modality");
  $el.empty(); // remove old options
  $.each(modalities, function(value, key) {
    $el.append($("<option></option>")
       .attr("value", key).text(key));
    });

}

function load_departments(departments){
  var $el = $("#departmentcode");
  $el.empty(); // remove old options
  $.each(departments, function(value, key) {
    $el.append($("<option></option>")
       .attr("value", key).text(key));
    });

}

function reset_departments(){
  $("#departmentcode").html('<option value="Choose">Choose</option>')
}

function reset_modalities(){
  $("#modality").html('<option value="Choose">Choose</option>')
}

function text_info(text){
  return '<span class = "text-info">'+text+'</span>';
}

function load_patient_info(patient_info){
  html = '<div class="panel panel-default">';
  html += '<div class="panel-heading">Patient Information</div>';
  html += '<div class="panel-body">';
  html += '<p>Name: '+text_info(patient_info.patient_id)+'</p>';
  html += '<p>Age: '+text_info(patient_info.age)+'</p>';
  html += '<p>Gender: '+text_info(patient_info.gender)+'</p>';
  html += '<p>Email: '+ text_info(patient_info.patient_id.slice(0,6)+"@gmail.com")+'</p>';
  //html += '<p>Phone number: '+text_info(patient_info.telephone)+'</p>';
  html += '</div></div></div>';
  $('#patient-info').html(html);
}

function load_charts(orgcode, modality){
  html = '<div> Is load_charts working? </div>';
  console.log(html);
}

function create_charts(orgcode, modality){

}