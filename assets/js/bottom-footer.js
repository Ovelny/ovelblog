window.onload = function() {
    var
       bodyHeight = document.body.offsetHeight,
       windowHeight = window.innerHeight,
       footer = document.getElementById("footer").style,
       inline_changes = {
           position: "absolute",
           bottom: "0",
           left: "0",
           right: "0",
           margin: "inherit",
           width: "inherit",
           padding: "inherit"
           }

    if (bodyHeight > windowHeight) {
        return false;
    }
    else {
        for (var property in inline_changes) {
            if (property in footer) footer[property] = inline_changes[property];
        }
    }
}
