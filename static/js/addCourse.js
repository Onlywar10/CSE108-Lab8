
function updateGrade(studentId, classId, inputElement) {
    const newGrade = inputElement.value;

    fetch(`/class/${classId}/update_grade`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            student_id: studentId,
            new_grade: newGrade,
        }),
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to update grade');
            }
            return response.json();
        })
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            alert('Error updating grade: ' + error.message);
            inputElement.focus();
        });
}