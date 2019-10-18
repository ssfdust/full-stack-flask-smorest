$('#fa_modal_window').on('shown.bs.modal', function () {
  // do something…
    var beattype = $('label[for=type').parent();
    var crontab = $('label[for=crontab]').parent();
    var interval = $('label[for=interval]').parent();
    var form = $('form[role=form]');
    var formarr = form.serializeArray();
    var curtype = '';
    for (i=0;i < formarr.length;i++){
        if (formarr[i]['name'] === 'type') {
            curtype = formarr[i]['value'];
        }
    }
    if (curtype === 'crontab'){
        interval.remove();
    } else {
        crontab.remove();
    }
    $('select#type').change(function(data) {
        if (data.val === 'crontab'){
            interval.remove();
            crontab.insertAfter(beattype);
        } else {
            crontab.remove();
            interval.insertAfter(beattype);
        }
    });
})
