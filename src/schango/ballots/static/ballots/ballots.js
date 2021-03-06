$(document).ready(function(){

    //////////////////
    // View details //
    //////////////////

    $(".show-more").click(function(){
        $(this).children().toggle();
        $(this).attr("for").split(" ").map(function(id){
            $("#" + id).toggle();
        });
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
            try {
                $(this).text(dt.toLocaleFormat());
            } catch(err) {
                $(this).text(dt.toLocaleString());
            }
        }
    });


    ///////////////////////
    // Dismiss Jumbotron //
    ///////////////////////

    $(".jumbo-dismiss").click(function(){
        $(this).closest(".jumbotron").slideUp("fast");
    });

});
