
    function previewImage(event) {
        var reader = new FileReader();
        reader.onload = function(){
            var output = document.getElementById('profile-picture-preview');
            output.src = reader.result;
        };
        reader.readAsDataURL(event.target.files[0]);
        document.querySelector('#id_profile_picture').files = event.target.files;
    }
