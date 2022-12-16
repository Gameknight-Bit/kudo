$(document).ready(
    $(function () {
        //when input's value changes
        $("#myFile").change(function () {
            if($(this).val())
            {
                $("#myBtn").prop("disabled", false);
            }
            else
            {
                
            }
        });
    })


);
