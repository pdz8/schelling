$(document).ready(function(){

    //////////////////
    // View details //
    //////////////////

    $(".show-more").click(function(){
        $(this).children().toggle();
        $("#" + $(this).attr("for")).toggle();
    });


    //////////////////
    // Localize UTC //
    //////////////////

    // Convert UTC seconds to DateTime strings
    $(".localize-utc,.localize-utc-short").each(function(){
        var dt = new Date(Number($(this).attr("utc")) * 1000);
        if ($(this).hasClass("localize-utc-short")) {
            $(this).text(dt.toLocaleDateString());
        } else {
            $(this).text(dt.toLocaleFormat());
        }
    });
});
