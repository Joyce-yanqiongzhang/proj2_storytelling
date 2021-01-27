var capture;
var video;
var hostpath = 'https://10.19.92.79:8001/'

function setup() {
  pic_canvas = createCanvas(window.innerWidth, window.innerHeight*0.85);
  pic_canvas.position = (0, 0);
  //pic_canvas.style = {float:left}
  video = createCapture(VIDEO);
  video.size(width, height);
  
  //image(video, 0, 0);
  video.hide();
  textAlign(RIGHT);      
  background(50);
}

function draw() {
     //video.show();
    filter('THRESHOLD');
    image(video,0,0,width,height);
          
    
}

function take_a_photo(){
  img = video.get();
  image(img,0,0);
  var button1 = document.getElementById('take_a_photo');
  var button2 = document.getElementById('retake_photo');
  var button3 = document.getElementById('confirm_photo');
  button1.style.display = 'none';
  button2.style.display = 'block';
  button3.style.display = 'block';
}

function retake_photo(){
  video = createCapture(VIDEO);
  video.size(width, height);
  video.hide();
  textAlign(RIGHT);
  //image(video, 0,0,width,height);
  var button1 = document.getElementById('take_a_photo');
  var button2 = document.getElementById('retake_photo');
  var button3 = document.getElementById('confirm_photo');
  button1.style.display = 'block';
  button2.style.display = 'none';
  button3.style.display = 'none';
}

function confirm_photo(){
  img_base64 = pic_canvas.elt.toDataURL('image/png');
  var data = new FormData();
  data.append('img_data', img_base64);
  function ajax() {
    $.ajax({
        url: "/upload_img/",
        type: "POST",
        dataType: "JSON",
        data: data,
        contentType: false,
        processData: false,
        success: function (res) {
          window.location.href = hostpath+'sepastory'
          //alert(res['img_url'])
            //var user_num = res['user_num'];
            //var user_img = res['img_url'];
            //var html = [];
            //html.push("<div class='row_container' id='user_container"+user_num+"'><img class='user_image' id='img_user"+ user_num +"' src='" +user_img+ "'><h4>    User"+user_num+"</h4></div>")
            //$("#character_container").append(html.join(""));
        }, error(error) {
            console.log('error: ', error)
        }
    });
}

ajax()


}

function map_characters(){
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
          //alert("123");
            var user_num = res['user_num'];
            
            cur_user = 1
            while (cur_user<=user_num) {
              html = []
              html.push("<div class='return_character_container'><h4>User analysis:</h4><h5>Gender: "+res['user'+cur_user+'gender']+"</h5><h5>Age: "+res['user'+cur_user+'age']+"</h5><h5>Facial features: </h5><p>"+res['user'+cur_user+'attributes']+"</p><h5>Overall score for the characters (prince, princess, wizard, rabbit): </h5><p>"+res['user'+cur_user+'score']+"</p><h3>User "+cur_user+" is a "+res['user'+cur_user+'character']+"!</h3></div>")
              $("#user_container"+cur_user).append(html.join(''));
              cur_user++;
            }
            
           
            
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
            //alert(res['storyline']);
            var environment_p = document.getElementById('environment');
            var character_p = document.getElementById('character');
            var storyline_p = document.getElementById('storyline');
            var story_p = document.getElementById('story');
            environment_p.innerHTML = res['environment'];
            character_p.innerHTML = res['characters'];
            storyline_p.innerHTML = res['storyline'];
            story_p.innerHTML = res['story'];

        }, error(error) {
            console.log('error: ', error)
        }
    });
  }

  ajax()

}

function add_user(){
  //video = createCapture(VIDEO);
  //video.size(width, height);
  //video.hide();
  //textAlign(RIGHT);
  var button_div1 = document.getElementById('button_div1');
  var button_div3 = document.getElementById('button_div3');
  button_div1.style.display = 'block';
  button_div3.style.display = 'none';
}