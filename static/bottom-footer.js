window.onload = function() {
    var bodyHeight = document.body.offsetHeight;
    var windowHeight = window.innerHeight;
    if(bodyHeight > windowHeight) {
        return false;
    }
    else {
        document.getElementById("footer").style.position = "absolute";
        document.getElementById("footer").style.bottom = "0";
        document.getElementById("footer").style.left = "0";
        document.getElementById("footer").style.right = "0";
        document.getElementById("footer").style.margin = "auto auto 1rem auto";
        document.getElementById("footer").style.width = "inherit";
        document.getElementById("footer").style.padding = "inherit";
    }
}