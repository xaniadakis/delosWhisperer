function downloadCourseByRid(rid, name) {
    alert("Requesting download of course: " + name)
    const options = {
        method: 'GET',
        mode: 'no-cors',
        cache: 'default',
    };
    const params = new URLSearchParams({
        rid: rid,
        name: name
    }).toString()
    const myRequest = new Request("http://localhost:8000/downloadCourse?" + params);

    fetch(myRequest, options)
        .then((response) => {
            console.log(response)
            return response.json();
        })
        .then(responseBody => {
            alert(responseBody);
        });
}
