$(document).ready(function(){

    // Enable detail views
    $(".show-more").click(function(){
        $(this).children().toggle();
        $("#" + $(this).attr("for")).toggle();
    });
});
