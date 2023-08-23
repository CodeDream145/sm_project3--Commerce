function adjustTextareaHeight(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
}

document.addEventListener('DOMContentLoaded', function () {
    const commentTextarea = document.getElementById('my_comment');
    const commentError = "{{ comment_error|default:'' }}"; 
 
    if (commentError) {
        adjustTextareaHeight(commentTextarea);
    }

    commentTextarea.addEventListener('input', function () {
        adjustTextareaHeight(this);
    });
});
