$(document).ready(function(){

    ///////////////////////////
    // Count characters left //
    ///////////////////////////

    $(".limited-chars").on("textChanged", function(){
        var cb = $(this).find(" textarea")[0].value.length;
        $(this).find(" .char-used").text(cb);
    });
    $(".limited-area textarea,textarea.limited-area").keyup(function(){
        $(this).closest(".limited-chars").trigger("textChanged");
    });
    $(".limited-chars").on("changeText", function(event, s){
        $(this).find(".limited-area textarea,textarea.limited-area")[0]
                .value = s;
        $(this).trigger("textChanged");
    });
    $(".limited-chars").trigger("textChanged");
    $(".limited-chars .char-max").text(
            $(".limited-chars textarea").first().attr("maxlength"));


    ///////////////////////
    // Dynamic poll form //
    ///////////////////////

    // Add options to poll
    $(".poll-form-options").on("addOption", function() {
        $(this).append('\
<li class="poll-form-option">\
    <input type="text" placeholder="Enter choice" class="form-control">\
</li>\
        ');
        $(this).children().last().find("input").keyup(function(){
            $(this).closest(".poll-form").trigger("recompute");
        });
    });
    $(".poll-form .poll-form-add").click(function(){
        $(this).closest(".poll-form").find(".poll-form-options")
                .trigger("addOption");
        $(this).closest(".poll-form").trigger("recompute");
    });
    $(".poll-form-options").trigger("addOption");
    $(".poll-form-options").trigger("addOption");

    // Remove options
    $(".poll-form .poll-form-rm").click(function(){
        var ls = $(this).closest(".poll-form").find(".poll-form-options")
                .children();
        if (ls.length > 2) {
            ls.last().remove();
        }
        $(this).closest(".poll-form").trigger("recompute");
    });

    // Compute question
    $(".poll-form textarea.poll-form-area").keyup(function(){
        $(this).closest(".poll-form").trigger("recompute");
    });
    $(".poll-form").on("recompute", function(){
        var s = $(this).find(" textarea.poll-form-area")[0].value;
        var i = 1;
        $(this).find(" .poll-form-options").children().each(function(){
            s += i + "~" + $(this).find(" input")[0].value;
            i++;
        });
        if ($(this).attr("for")) {
            $("#" + $(this).attr("for")).trigger("changeText",[s]);
        }
    });
    $(".poll-form").trigger("recompute");


    /////////////////////
    // DateTime picker //
    /////////////////////

    // Initialize
    $(".date").datetimepicker();

    // Update Django form field with UTC time
    $(".date").on("dp.change", function(){
        var target_id = $(this).attr("for");
        if (target_id) {
            var mom = $(this).data("DateTimePicker").date();
            $("#" + target_id)[0].value = Math.round(mom.valueOf() / 1000);
        }
        
    });

});

