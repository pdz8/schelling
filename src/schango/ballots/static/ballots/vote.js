$(document).ready(function(){

    // Enable all the Ethereum details to be read
    var switcher = $("#show_more");
    switcher.click(function(){
        if (switcher.text() == "Show more") {
            switcher.text("Show less")
        } else {
            switcher.text("Show more")
        }
        $("#tech_panel").toggle();
    });
});
