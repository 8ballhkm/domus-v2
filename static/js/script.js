'use strict';

/**
 * element toggle function
 */

const elemToggleFunc = function (elem) { elem.classList.toggle("active"); }



/**
 * navbar toggle
 */

const navbar = document.querySelector("[data-navbar]");
const overlay = document.querySelector("[data-overlay]");
const navCloseBtn = document.querySelector("[data-nav-close-btn]");
const navOpenBtn = document.querySelector("[data-nav-open-btn]");
const navbarLinks = document.querySelectorAll("[data-nav-link]");

const navElemArr = [overlay, navCloseBtn, navOpenBtn];

/**
 * close navbar when click on any navbar link
 */

for (let i = 0; i < navbarLinks.length; i++) { navElemArr.push(navbarLinks[i]); }

/**
 * addd event on all elements for toggling navbar
 */

for (let i = 0; i < navElemArr.length; i++) {
  navElemArr[i].addEventListener("click", function () {
    elemToggleFunc(navbar);
    elemToggleFunc(overlay);
  });
}



/**
 * header active state
 */

const header = document.querySelector("[data-header]");

window.addEventListener("scroll", function () {
  window.scrollY >= 400 ? header.classList.add("active")
    : header.classList.remove("active");
}); 

/**
 *  Live chat
 */
console.log("Chat script loaded");

let chatPanelOpen = false;
let chatSocket = null;
let currentRoomName = null;
let currentPartnerId = null;
let currentPartnerName = null;

function toggleChatPanel() {
  const panel = document.getElementById('chat-panel');
  chatPanelOpen = !chatPanelOpen;
  panel.style.display = chatPanelOpen ? 'flex' : 'none';

  if (chatPanelOpen) {
    loadChatRooms();
  } else {
    closeChat();
  }
}

function loadChatRooms() {
  const roomsList = document.getElementById('chat-rooms-list');
  roomsList.innerHTML = 'Loading chats...';

  fetch('/api/chat/rooms/')
    .then(res => res.json())
    .then(data => {
      if (data.partners.length === 0) {
        roomsList.innerHTML = '<p>No chats yet.</p>';
        return;
      }
      roomsList.innerHTML = '';
      data.partners.forEach(partner => {
        const btn = document.createElement('button');
        btn.textContent = partner.username + ': ' + partner.last_message.slice(0, 30);
        btn.style.display = 'block';
        btn.style.width = '100%';
        btn.style.textAlign = 'left';
        btn.style.marginBottom = '5px';
        btn.onclick = () => openChatRoom(partner.id, partner.username);
        roomsList.appendChild(btn);
      });
    })
    .catch(() => {
      roomsList.innerHTML = '<p>Error loading chats.</p>';
    });
}

function startChat(ownerId) {
  const currentUserId = window.currentUserId;
  
  if (!currentUserId || currentUserId === "null") {
    alert("Please log in to chat.");
    return;
  }
  

  const roomName = currentUserId < ownerId
    ? `${currentUserId}_${ownerId}`
    : `${ownerId}_${currentUserId}`;
  

  toggleChatPanel();
  openChatRoom(ownerId, `User ${ownerId}`);  
}

async function openChatRoom(partnerId, partnerUsername) {
  const currentUserId = window.currentUserId;
  if (
    !currentUserId || 
    currentUserId === "null" ||
    currentUserId === "undefined" ||
    currentUserId === 0) {
    alert('Please log in to chat.');
    return;
  }

  if (chatSocket) {
    chatSocket.close();
  }

  currentPartnerId = partnerId;
  currentPartnerName = partnerUsername;
  currentRoomName = currentUserId < partnerId ? `${currentUserId}_${partnerId}` : `${partnerId}_${currentUserId}`;


  document.getElementById('chat-window').style.display = 'flex';
  document.getElementById('chat-header').textContent = `Chat with ${partnerUsername}`;
  document.getElementById('chat-messages').innerHTML = '';

  const messagesContainer = document.getElementById('chat-messages');
  messagesContainer.innerHTML = 'Loading chat history...';


  try {
    const response = await fetch(`/api/chat/history/${partnerId}/`);
    const data = await response.json();

    messagesContainer.innerHTML = ''; 

    data.messages.forEach(msg => {
      const msgDiv = document.createElement('div');
      msgDiv.textContent = `${msg.sender_username}: ${msg.content}`;
      messagesContainer.appendChild(msgDiv);
    });

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  } catch (error) {
    messagesContainer.innerHTML = '<div style="color: red;">Failed to load chat history.</div>';
    console.error('Failed to load chat history:', error);
  }

  
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/chat/${currentRoomName}/`;
  
  console.log('Connecting to WebSocket:', wsUrl);
  chatSocket = new WebSocket(wsUrl);

  chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    const messages = document.getElementById('chat-messages');
    messages.innerHTML += `<div>${data.message}</div>`;
    messages.scrollTop = messages.scrollHeight;
  };

  chatSocket.onerror = function(e) {
    console.error('Chat socket error:', e);
  };

  chatSocket.onclose = function() {
    console.log('Chat socket closed');
  };
}

function sendMessage() {
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (message && chatSocket && chatSocket.readyState === WebSocket.OPEN) {
    chatSocket.send(JSON.stringify({ message }));
    input.value = '';
  }
  else{
    console.log("Message not sent. WebSocket readyState:", chatSocket ? chatSocket.readyState : "No socket");
  }
}

function closeChat() {
  if (chatSocket) {
    chatSocket.close();
    chatSocket = null;
  }
  document.getElementById('chat-window').style.display = 'none';
  document.getElementById('chat-messages').innerHTML = '';
}

async function loadChatHistory(partnerId) {
  const messagesContainer = document.getElementById('chat-messages');
  messagesContainer.innerHTML = 'Loading...';

  try {
    const response = await fetch(`/api/chat/history/${partnerId}/`);
    const data = await response.json();

    messagesContainer.innerHTML = '';
    data.messages.forEach(msg => {
      const msgDiv = document.createElement('div');
      msgDiv.textContent = `${msg.sender_username}: ${msg.content}`;
      messagesContainer.appendChild(msgDiv);
    });

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  } catch (error) {
    messagesContainer.innerHTML = 'Failed to load messages.';
    console.error('Error loading chat history:', error);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chat-input');
  if (input) {
    input.addEventListener('keydown', function(event) {
      if (event.key === 'Enter') {
        event.preventDefault();  
        sendMessage();
      }
    });
  }
});
 

/**
 * Property Image
 */
let currentImageIndex = 0;  
let images = JSON.parse(document.getElementById('imageUrls').textContent);



function openModal() {
    document.getElementById("imageModal").style.display = "block";
    displayImage(currentImageIndex);  
}


function closeModal() {
    document.getElementById("imageModal").style.display = "none";
    displayImage(currentImageIndex);
}


function changeImage(direction) {
    currentImageIndex += direction;

    
    if (currentImageIndex >= images.length) {
        currentImageIndex = 0;  
    } else if (currentImageIndex < 0) {
        currentImageIndex = images.length - 1;  
    }

    displayImage(currentImageIndex);  
}


function displayImage(index) {
    const modalImage = document.getElementById("modalImage");
    modalImage.src = images[index];
}



function toggleDeleteIndicator(checkbox, imageId) {
    const imageItem = document.getElementById(`image-item-${imageId}`);
    const checkmark = document.getElementById(`checkmark-${imageId}`);
    
    
    if (checkbox.checked) {
        checkmark.style.display = 'inline';  
        imageItem.style.backgroundColor = '#f8f9fa';  
    } else {
        checkmark.style.display = 'none'; 
        imageItem.style.backgroundColor = '';  
      }
}


function openFeatureModal() {
    var featureModal = document.getElementById("featureModal"); 
    featureModal.style.display = "block";  
}


function closeFeatureModal() {
    var featureModal = document.getElementById("featureModal"); 
    featureModal.style.display = "none";  
}


document.addEventListener("DOMContentLoaded", function () {
    var closeButton = document.querySelector(".close-feature");

    if (closeButton) {
        closeButton.onclick = function() {
            closeFeatureModal();
        };
    }

  
    window.onclick = function(event) {
        var featureModal = document.querySelector(".feature-modal");
        if (event.target === featureModal) {
            closeFeatureModal();
        }
    }

    document.getElementById("modalFeatureForm").onsubmit = function (event) {
        event.preventDefault();

        var selectedFeatures = [];
        var checkboxes = document.querySelectorAll('input[name="features[]"]:checked');
        checkboxes.forEach(function (checkbox) {
            selectedFeatures.push(checkbox.value);
        });


        if (selectedFeatures.length === 0) {
            alert("Please select at least one feature.");
            return;
        }

        var featureInput = document.createElement("input");
        featureInput.type = "hidden";
        featureInput.name = "features"; 
        featureInput.value = selectedFeatures.join(',');
        document.querySelector('form').appendChild(featureInput);

        
        closeFeatureModal();
        document.querySelector('form').submit();
    };
});
}
