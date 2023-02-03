
$(document).ready(function(){
    $('#signup-form').on('submit', function(event){
        event.preventDefault();

        $.ajax({
            url: "{% url 'register' %}",
            type: 'POST',
            // headers: {'X-CSRFToken': '{{ csrf_token }}'},
            data: $('#signup-form').serialize(),
            
            beforeSend: function () {
                $("#signup").modal("show");
            },
            
            success: function(data) {
                $('#signup .modal-body').html(data);
            }
        });
    });
});