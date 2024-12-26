let userId = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    userId = localStorage.getItem('userId');
    if (userId) {
        document.getElementById('auth').style.display = 'none';
        document.getElementById('app').style.display = 'block';
        fetchNotes();
    }
});

function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    fetch('http://127.0.0.1:5000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.user_id) {
            userId = data.user_id;
            localStorage.setItem('userId', userId);
            document.getElementById('auth').style.display = 'none';
            document.getElementById('app').style.display = 'block';
            fetchNotes();
        } else {
            alert('Invalid credentials');
        }
    });
}

function signup() {
    const username = document.getElementById('signupUsername').value;
    const password = document.getElementById('signupPassword').value;
    fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'User registered successfully') {
            alert('User registered successfully. Please login.');
        } else {
            alert(data.message);
        }
    });
}

function fetchNotes() {
    fetch(`http://127.0.0.1:5000/notes?user_id=${userId}`)
        .then(response => response.json())
        .then(data => {
            const notesList = document.getElementById('notesList');
            notesList.innerHTML = '';
            data.forEach(note => {
                const li = document.createElement('li');
                li.textContent = note.title;
                const viewButton = document.createElement('button');
                viewButton.textContent = 'View';
                viewButton.onclick = () => viewNote(note.id);
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.onclick = () => deleteNote(note.id);
                li.appendChild(viewButton);
                li.appendChild(deleteButton);
                notesList.appendChild(li);
            });
        });
}

function addNote() {
    const noteInput = document.getElementById('noteInput');
    const note = { user_id: userId, title: noteInput.value, content: '' };
    fetch('http://127.0.0.1:5000/notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(note)
    })
    .then(response => response.json())
    .then(() => {
        noteInput.value = '';
        fetchNotes();
    });
}

function viewNote(noteId) {
    fetch(`http://127.0.0.1:5000/notes/${noteId}?user_id=${userId}`)
        .then(response => response.json())
        .then(note => {
            document.getElementById('noteTitle').value = note.title;
            document.getElementById('noteContent').value = note.content;
            document.getElementById('noteEditor').style.display = 'block';
            document.getElementById('app').style.display = 'none';
            document.getElementById('saveNote').onclick = () => saveNote(noteId);
        });
}

function saveNote(noteId) {
    const noteTitle = document.getElementById('noteTitle').value;
    const noteContent = document.getElementById('noteContent').value;
    const note = { user_id: userId, title: noteTitle, content: noteContent };
    fetch(`http://127.0.0.1:5000/notes/${noteId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(note)
    })
    .then(response => response.json())
    .then(() => {
        closeEditor();
        fetchNotes();
    });
}

function closeEditor() {
    document.getElementById('noteEditor').style.display = 'none';
    document.getElementById('app').style.display = 'block';
}

function deleteNote(noteId) {
    fetch(`http://127.0.0.1:5000/notes/${noteId}?user_id=${userId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(() => {
        fetchNotes();
    });
}

function logout() {
    localStorage.removeItem('userId');
    userId = null;
    document.getElementById('auth').style.display = 'block';
    document.getElementById('app').style.display = 'none';
}