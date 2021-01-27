$(document).ready(function(){ 
    setInterval(update_content, 200);
    }) 

function take_picture(){
    window.location.href = "https://10.19.92.79:8001/take_photo/";
}


function map_character(){
    var data = new FormData();
    function ajax() {
        $.ajax({
            url: "/map_character/",
            type: "POST",
            dataType: "JSON",
            data: data,
            contentType: false,
            processData: false,
            success: function (res) {
                
            }, error(error) {
                console.log('error: ', error)
            }
        });
    }

    ajax()
}

function generate_story(){
    var data = new FormData();
    function ajax() {
        $.ajax({
            url: "/generate_story/",
            type: "POST",
            dataType: "JSON",
            data: data,
            contentType: false,
            processData: false,
            success: function (res) {
                
            }, error(error) {
                console.log('error: ', error)
            }
        });
    }

    ajax()
}

function update_content(){
    var data = new FormData();
    function ajax() {
        $.ajax({
            url: "/update_content/",
            type: "POST",
            dataType: "JSON",
            data: data,
            contentType: false,
            processData: false,
            success: function (res) {
                //alert("123");
                var user_num = res['user_num'];
                var is_mapped = res['is_mapped'];
                var is_story = res['is_story'];

                var user_photos = res['user_photos'].split(',');
                var characters = res['characters'].split(',');
                var storyline = res['storyline'];
                var story = res['story'];

                //var user_div = document.getElementById('user_container');   
                $("#user_container").empty();          
                cur_user = 1
                while (cur_user<=user_num) {
                html = []
                html.push("<div class='row_subcontainer' id='userbox"+cur_user+"'><div class='img_box'><img class='user_image' src='"+ user_photos[cur_user-1] +"'></div><h5>User "+cur_user+"</h5></div>")
                $("#user_container").append(html.join(''));
                cur_user++;
                }
                //alert(is_mapped)

                if(is_mapped=='1') {
                    cur_user = 1;
                    while(cur_user<=user_num) {
                        html = []
                        html.push("<h5>User"+cur_user+" is a "+characters[cur_user-1]+"!</h5>")
                        //alert($("#userbox"+cur_user));
                        $("#userbox"+cur_user).append(html.join(''));
                        cur_user++;
                    }
                }

                if(is_story=='1') {
                    var storyline_container = document.getElementById('storyline_container');
                    var story_container = document.getElementById('story_container');
                    var storyline_content = document.getElementById('storyline');
                    var story_content = document.getElementById('story');
                    storyline_container.style.display = "block";
                    story_container.style.display = "block";
                    storyline_content.innerHTML = storyline;
                    story_content.innerHTML = story;
                    
                }
                
            
                
            }, error(error) {
                console.log('error: ', error)
            }
        });
    }

    ajax()
}