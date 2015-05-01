$(document).ready(function () {
    $("body").keydown(function(e) {
        if(e.which == 37) { // left
            current_page = $("#current_page").html();
            $("#left_button_" + current_page).trigger("click");
        }
        else if(e.which == 39) { // right
            current_page = $("#current_page").html();
            $("#right_button_" + current_page).trigger("click");
        }
    });
    $("div.right_button").on("click",function(){
        // page right
        num_of_pages = $("#total_number_of_pages").attr("value");
        page_id = $(this).attr('value');
        //$('.results').html(page_id );
        $("#page_" + page_id).toggle();
        page_id++;
        if (page_id > num_of_pages) {
            page_id = 1
        }
        $("#page_" + page_id).toggle();
        $("#current_page").text(page_id);
    });
    $("div.left_button").on("click",function(){
        // page left
        num_of_pages = $("#total_number_of_pages").attr("value");
        page_id = $(this).attr('value');
        //$('.results').html(page_id );
        $("#page_" + page_id).toggle();
        page_id--;
        if (page_id < 1) {
            page_id = num_of_pages
        }
        $("#page_" + page_id).toggle();
        $("#current_page").text(page_id);
    });
});
//end of line
