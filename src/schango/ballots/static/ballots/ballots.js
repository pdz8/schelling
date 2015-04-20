$(document).ready(function(){

    // Enable detail views
    $(".show-more").click(function(){
        $(this).children().toggle();
        $("#" + $(this).attr("for")).toggle();
    });

    // Count characters left
    $(".limited-chars textarea").keyup(function(){
        $(this).closest(".limited-chars").find(" .char-used")
                .text(String(this.value.length));
    });
    $(".limited-chars textarea").keyup();
    $(".limited-chars .char-max").text(
            $(".limited-chars textarea").first().attr("maxlength"));
});
