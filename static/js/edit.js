function getExtension(filename){
    var parts = filename.split('.');
    return parts[parts.length - 1];
}

function isImage(filename){
    var ext = getExtension(filename);
    switch (ext.toLowerCase()) {
        case 'jpg':
        case 'gif':
        case 'bmp':
        case 'png':
            //add more valid extensions here
            return true;
    }
    return false;
}

function file_changed(){ //mutator method!!!
    //updating profile picture
    var selectedFile = document.getElementById('upload-form').files[0];
    var img = document.getElementById('edit-profile-img')

    var reader = new FileReader();
    reader.onload = function(){
        img.src = this.result
    }
    reader.readAsDataURL(selectedFile)
}

$(function(){ //Runs on startup
    $("#submit-button").click(function(){
        function failValidation(msg){
            alert(msg); //do some other fancy stuff instead!!!
            return false;
        }

        ////////// Validate Img ////////
        var file = $('#upload-form')
        if (!isImage(file.val())){
            return failValidation('Profile Pictures can only have extensions .jpg, .png, or .gif');
        }

        ////// SUCCESS!!! //////
        alert('Valid File! Lets return true and send a post request to the server!')
        const formData = new FormData();
        formData.append('username', $('#name-input').val()); //Append UserName
        formData.append('status', $('#kudos-message').val()); //Append StatusMessage
        formData.append('file', file.val()); 

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/user/{{User.UserId}}/edit', true)
        xhr.send(formData)

        return false;
    });
});