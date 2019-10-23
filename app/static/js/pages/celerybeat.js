$("#fa_modal_window").on("shown.bs.modal", function () {
    var beattype = $("label[for=type").parent().parent();
    var crontab = $("label[for=crontab]").parent().parent();
    var interval = $("label[for=interval]").parent();
    var form = $("form[role=form]");
    var formarr = form.serializeArray();
    var curtype = "";
    for (i=0;i < formarr.length;i++){
        if (formarr[i].name === "type") {
            curtype = formarr[i].value;
        }
    }
    interval.remove();
    crontab.remove();
    if (curtype === "crontab"){
        crontab.insertAfter(beattype);
    } else {
        interval.insertAfter(beattype);
    }
    $("select#type").change(function(data) {
        var val = data.currentTarget.value;
        if (val === "crontab"){
            interval.remove();
            crontab.insertAfter(beattype);
        } else {
            crontab.remove();
            interval.insertAfter(beattype);
        }
    });
})
