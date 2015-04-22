$(document).ready(
    function() {
        $(function(){
            $("body").on("click","div.right_button", 
                function(){
                    num_of_pages = $("#total_number_of_pages").attr("value")
                    page_id = $(this).attr('value');
                    //$('.results').html(page_id );
                    $("#page_" + page_id).toggle();
                    page_id++;
                    if (page_id > num_of_pages) {
                        page_id = 1
                    }
                    $("#page_" + page_id).toggle();
                }
            );
        });
        $(function(){
            $("body").on("click","div.left_button", 
                function(){
                    num_of_pages = $("#total_number_of_pages").attr("value")
                    page_id = $(this).attr('value');
                    //$('.results').html(page_id );
                    $("#page_" + page_id).toggle();
                    page_id--;
                    if (page_id < 1) {
                        page_id = num_of_pages
                    }
                    $("#page_" + page_id).toggle();
                }
            );
        });
    }
);
//end of line
