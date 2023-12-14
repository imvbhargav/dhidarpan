function show_content(i, model){
    if (model == "reply-form"){
    rf = document.getElementById("reply-form-" + i);
        if (rf.style.display == "none"){
        rf.style.display = "block";
        }
        else{
        rf.style.display = "none";
        }
    }
    else if (model == "comment-form"){
        c = document.getElementById("comment-box");
        if (c.style.display == "none"){
        c.style.display = "block";
        }
        else{
        c.style.display = "none";
        }
    }
    else if (model == "replies"){
        rep = document.getElementById("reply-box-" + i);
        if (rep.style.display == "none"){
        rep.style.display = "block";
        }
        else{
        rep.style.display = "none";
        }
    }

}
let mybutton = document.getElementById("btt");
window.onscroll = function(){scrollFunction()};
function scrollFunction(){
    if (document.body.scrollTop>20 || document.documentElement.scrollTop>20){
        mybutton.style.display="block";
    }
    else{
        mybutton.style.display="none";
    }
}

function topfunc(){
    document.body.scrollTop=0;
    document.documentElement.scrollTop=0;
}