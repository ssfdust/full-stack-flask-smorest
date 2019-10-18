const Toast = Swal.mixin({
  toast: true,
  position: 'top-end',
  showConfirmButton: false,
  timer: 3000
});

$('#avator-overlay').on('click', function(){
  $("#fileToUpload").click();
})
$('#avator-overlay').hover(function(){
  $('#avator-overlay').animate({opacity: 1}, 300);
}, function () {
  $('#avator-overlay').animate({opacity: 0.0}, 300);
})

$('#fileToUpload').on('change', function(){
  var formData = new FormData();
  formData.append("file",$("#fileToUpload")[0].files[0]);
  $.ajax({  
        url : '/admin/profile/upload-avator',  
        type : 'POST',  
        data : formData,  
        // 告诉jQuery不要去处理发送的数据
        processData : false, 
        // 告诉jQuery不要去设置Content-Type请求头
        contentType : false,
        success : function(res) { 
            if(res.code === 0){
              var imgUrl = $('.usr-avator').attr('src');
              $('.usr-avator').attr('src', imgUrl + '?' + new Date().getTime());
            }else{
                console.log("失败");
            }
        },  
        error : function(responseStr) { 
            console.log("error");
        }  
    }); 
})

$('#savePassword').on('click', function(){
    if ($('#passwdForm')[0].checkValidity() === true)
    {
        var data = $('#passwdForm').serializeJSON();
        console.log(data);
        $.ajax({
          type: "patch",
          dataType: "json",
          url: '/admin/profile/set-passwd',
          data: JSON.stringify(data),
          contentType: "application/json; charset=utf-8",
          success: function(data) {
            if (data.code == 1){
                Toast.fire({
                  type: 'error',
                  title: '初始密码错误'
                });
            } else {
                Toast.fire({
                  type: 'success',
                  title: '修改成功'
                });
                $('#modal-default').modal('toggle');
            }
          }
        });
    } else {
      $('#passwdForm')[0].reportValidity();
    }
})
