// Show Comment Button
function show_content(i, model){
    if (model == "reply-form"){
    rf = document.getElementById("reply-form-" + i);
    displayToggle(rf);
    }
    else if (model == "comment-form"){
        c = document.getElementById("comment-box");
        displayToggle(c);
    }
    else if (model == "replies"){
        rep = document.getElementById("reply-box-" + i);
        displayToggle(rep);
    }

}
function displayToggle(element){
    if (element.classList.contains("pd-none")){
        element.classList.remove("pd-none");
        element.classList.add("pd-block");
    }
    else{
        element.classList.remove("pd-block")
        element.classList.add("pd-none");
    }
}



// Go To Top Button
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



// Mobile Nav-bar Button
const bbtn = document.getElementById("burger-btn");
bbtn.addEventListener('click', function openNav(){
    const mn = document.getElementById("mbl-nav");
    const isOpen = bbtn.getAttribute('aria-expanded') === 'true';
    mn.classList.contains("ni-active") ? mn.classList.remove("ni-active") :  mn.classList.add("ni-active");
    isOpen ? bbtn.setAttribute('aria-expanded','false') : bbtn.setAttribute('aria-expanded','true');   
})