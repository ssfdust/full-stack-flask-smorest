/*
 * Author: Abdullah A Almsaeed
 * Date: 4 Jan 2014
 * Description:
 *      This is a demo file used only for the main dashboard (index.html)
 **/

$(function () {

  'use strict'
          
  const Toast = Swal.mixin({
      toast: true,
      position: 'top-end',
      showConfirmButton: false,
      timer: 3000
    });

  // Make the dashboard widgets sortable Using jquery UI
  $('.connectedSortable').sortable({
    placeholder         : 'sort-highlight',
    connectWith         : '.connectedSortable',
    handle              : '.card-header, .nav-tabs',
    forcePlaceholderSize: true,
    zIndex              : 999999
  })
  $('.connectedSortable .card-header, .connectedSortable .nav-tabs-custom').css('cursor', 'move')

  $('#dueDate').daterangepicker({
      singleDatePicker: true,
      timePicker: true,
      timePicker24Hour: true,
      timePickerIncrement: 30,
      locale: {
        format: 'YYYY-MM-DD HH:mm:ss' 
      }
    })

  // declear todoList
  $('.todo-list').data(
    {
      onCheck: function onCheck(item) {
        var itemId = event.target.id.replace('todoCheck', '');
        $.ajax({
          type: "patch",
          dataType: "json",
          url: '/admin/todolist/',
          data: JSON.stringify({'id': itemId, 'state': true}),
          contentType: "application/json; charset=utf-8",
          success: function(data) {
            Toast.fire({
              type: 'success',
              title: '完成任务'
            });
          }
        });
      },
      onUnCheck: function onUnCheck(item) {
        var itemId = event.target.id.replace('todoCheck', '');
        $.ajax({
          type: "patch",
          dataType: "json",
          url: '/admin/todolist/',
          data: JSON.stringify({'id': itemId, 'state': false}),
          contentType: "application/json; charset=utf-8",
          success: function(data) {
            Toast.fire({
              type: 'success',
              title: '撤销完成'
            });
          }
        });
      }
    }
  );
  $('.todo-list').attr('data-widget', 'todo-list');
  $('.todo-list').TodoList();

  // todolist List Plugin Options
  var todoOptions = {
    listClass: 'todo-list',
    valueNames: [
      {data: ['id', 'sort', 'level']},
      'text',
      'badge',
      {attr: 'name', name: 'todo-name'},
      {attr: 'checked', name: 'todo-checked'},
      {attr: 'id', name: 'todo-id'},
      {attr: 'for', name: 'todo-for'}
    ]
  };
  var todoList = new List('todo-listjs', todoOptions);
  var todoModal = $('#modal-default');
  var todoForm = $('#todoForm');
  var modalTitle = todoModal.find('h4.modal-title');
  var todoPage = 2;

  function getTodoForm(){
    var data = todoForm.serializeJSON();
    return {
      'id': data.todoId? data.todoId: null,
      'message': data.todoMessage,
      'due': data.todoDue
    }
  }

  function setTodoForm(itemValues) {
    var todoIdField = $('#todoId');
    var todoMessageField = $('#todoMessage');
    var todoDueDateField = $('#dueDate');
    todoIdField.val(itemValues['id']);
    todoMessageField.val(itemValues['message']);
    todoDueDateField.val(itemValues['due']);
  }

  todoModal.on('hidden.bs.modal', function (){
    setTodoForm({'id': '', 'message': '', 'due': ''})
    modalTitle.text('新增待办');
  });

  function hookTodoFunc(){
    $('.todo-list').find('input:checkbox:checked').parents('li').toggleClass('done');
    $('li[data-level=7]>small').addClass('badge-info');
    $('li[data-level=6]>small').addClass('badge-danger');
    $('li[data-level=5]>small').addClass('badge-warning');
    $('li[data-level=4]>small').addClass('badge-success');
    $('li[data-level=3]>small').addClass('badge-primary');
    $('li[data-level=2]>small').addClass('badge-secondary');
    $('li[data-level=1]>small').addClass('badge-thirdly');
    $('.todo-list>li>.tools>.fa-edit').click(function() {
      var itemId = $(this).closest('li').attr('data-id');
      var itemValues = todoList.get('id', itemId)[0].values();
      setTodoForm(itemValues);
      modalTitle.text('编辑待办');
      todoModal.modal();
    });
    $('.todo-list>li>.tools>.fa-trash').click(function() {
      var itemId = $(this).closest('li').attr('data-id');
      $.ajax({
        type: "delete",
        dataType: "json",
        url: '/admin/todolist/items',
        data: JSON.stringify({'id': itemId}),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
          Toast.fire({
            type: 'success',
            title: '删除成功'
          });
          getTodoList(todoPage);
        }
      });
    });
  }
  var todoPagination = $('#todo-pagination').pagination({
    dataSource: '/admin/todolist/items',
    locator: 'data',
    alias: {
      pageNumber: 'page',
      pageSize: 'per_page'
    },
    afterInit: function(item){
      console.log();
    },
    pageSize: 6,
    className: 'card-tools',
    ulClassName: 'pagination pagination-sm',
    totalNumberLocator: function (res){
      return res.meta.total
    },
    callback: function(data, pagination) {
      /* var pageData = $('#todo-pagination').data('pagination');
       * pageData.model.pageNumber = pagination */
      // template method of yourself
      todoPage = pagination.pageNumber;
      todoList.clear();
      for (var i=0;i < data.length; i++){
        var item = data[i];
        item['todo-for'] = 'todoCheck' + item.id;
        item['todo-checked'] = item.state?"checked": "no";
        item['todo-name'] = 'todo' + item.id;
        item['todo-id'] = 'todoCheck' + item.id;
        item['text'] = item.message;
        item['badge'] = '<i class="far fa-clock"></i> ' + item.rest_time;
        todoList.add(item);
      }
      $("input[checked='no']").prop('checked', false);
      hookTodoFunc()
    }
  });

  function getTodoList(page) {
    todoPagination.pagination('go', page);
  }

  $('#saveTodo').on('click', function (){
    if (todoForm[0].checkValidity() === true){
      $.ajax({
        type: "post",
        dataType: "json",
        url: '/admin/todolist/items',
        data: JSON.stringify(getTodoForm()),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
          Toast.fire({
            type: 'success',
            title: '保存成功'
          });
          if (getTodoForm()['id']){
            getTodoList(todoPage);
          } else {
            getTodoList(1);
          }
          todoModal.modal('toggle');
        }
      });
    } else {
      todoForm[0].reportValidity();
    }
  })

  // jQuery UI sortable for the todo list
  $('.todo-list').sortable({
    placeholder         : 'sort-highlight',
    handle              : '.handle',
    forcePlaceholderSize: true,
    zIndex              : 999999,
    update: function(event, ui ) {
      var list = $('.todo-list').children();
      var sortList = [];
      var todoIdList = [];
      for (var i=0;i < list.length;i++){
        sortList.push($(list[i]).attr('data-sort'));
      }
      sortList = sortList.sort().reverse();
      for (var i=0;i < list.length;i++){
        $(list[i]).attr('data-sort', sortList[i]);
        todoIdList.push({
          'id': $(list[i]).attr('data-id'),
          'sort': sortList[i]
        });
      }
      $.ajax({
        type: "patch",
        dataType: "json",
        url: '/admin/todolist/',
        data: JSON.stringify({'data': todoIdList}),
        contentType: "application/json; charset=utf-8",
        success: function(data) {
        }
      });
    }
  });

  // bootstrap WYSIHTML5 - text editor
  $('.textarea').summernote()

  /* jQueryKnob */
  $('.knob').knob()

  /* Chart.js Charts */
  // Sales chart
  var salesChartCanvas = document.getElementById('revenue-chart-canvas').getContext('2d');
  //$('#revenue-chart').get(0).getContext('2d');

  $.ajax(
    {
      url:"/admin/statistic/visit/",
      success:function(result){
        var salesChartData = {
          labels  : result.daily_stat.labels,
          datasets: [
            {
              label               : 'Digital Goods',
              backgroundColor     : 'rgba(60,141,188,0.9)',
              borderColor         : 'rgba(60,141,188,0.8)',
              pointRadius          : false,
              pointColor          : '#3b8bba',
              pointStrokeColor    : 'rgba(60,141,188,1)',
              pointHighlightFill  : '#fff',
              pointHighlightStroke: 'rgba(60,141,188,1)',
              data                :  result.daily_stat.cnts
            }
          ]
        };
        var salesChartOptions = {
          maintainAspectRatio : false,
          responsive : true,
          legend: {
            display: false
          },
          scales: {
            xAxes: [{
              gridLines : {
                display : false,
              }
            }],
            yAxes: [{
              gridLines : {
                display : false,
              }
            }]
          }
        };
        // This will get the first returned node in the jQuery collection.
        var salesChart = new Chart(salesChartCanvas, { 
            type: 'line', 
            data: salesChartData, 
            options: salesChartOptions
          }
        );
        // Donut Chart
        var pieChartCanvas = $('#sales-chart-canvas').get(0).getContext('2d')
        var pieData        = {
          labels: result.method_stat.labels,
          datasets: [
            {
              data: result.method_stat.values,
              backgroundColor : result.method_stat.colors,
            }
          ]
        }
        var pieOptions = {
          legend: {
            display: false
          },
          maintainAspectRatio : false,
          responsive : true,
        }
        //Create pie or douhnut chart
        // You can switch between pie and douhnut using the method below.
        var pieChart = new Chart(pieChartCanvas, {
          type: 'doughnut',
          data: pieData,
          options: pieOptions      
        });
      }
    });


  $.ajax(
    {
      url:"/admin/statistic/tasks/",
      success:function(result){
        // Sales graph chart
        var salesGraphChartCanvas = $('#line-chart').get(0).getContext('2d');
        //$('#revenue-chart').get(0).getContext('2d');

        var salesGraphChartData = {
          labels  : result.task_stat.labels,
          datasets: [
            {
              label               : '任务量',
              fill                : false,
              borderWidth         : 2,
              lineTension         : 0,
              spanGaps : true,
              borderColor         : '#efefef',
              pointRadius         : 3,
              pointHoverRadius    : 7,
              pointColor          : '#efefef',
              pointBackgroundColor: '#efefef',
              data                : result.task_stat.cnts
            }
          ]
        }

        var salesGraphChartOptions = {
          maintainAspectRatio : false,
          responsive : true,
          legend: {
            display: false,
          },
          scales: {
            xAxes: [{
              ticks : {
                fontColor: '#efefef',
              },
              gridLines : {
                display : false,
                color: '#efefef',
                drawBorder: false,
              }
            }],
            yAxes: [{
              ticks : {
                stepSize: 5000,
                fontColor: '#efefef',
              },
              gridLines : {
                display : true,
                color: '#efefef',
                drawBorder: false,
              }
            }]
          }
        }

        // This will get the first returned node in the jQuery collection.
        var salesGraphChart = new Chart(salesGraphChartCanvas, { 
            type: 'line', 
            data: salesGraphChartData, 
            options: salesGraphChartOptions
          }
        )
      }
    });

  $('#sendEmail').click(
    function(event){
      var emailInfo = $('#emailForm').serializeArray();
      var emailContent = $('.textarea').val();
      var data = {
        'emailto': emailInfo[0].value,
        'subject': emailInfo[1].value,
        'content': emailContent
      };
      $.ajax(
        {
          url: "/admin/send-mail/",
          data: data,
          type: 'POST',
          success: function(result){
          }
        }
      );
    }
  );

})
