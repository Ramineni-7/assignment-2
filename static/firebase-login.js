import { initializeApp } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-app.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/9.22.2/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyAe1sOhlR9D0ramO_TFef5LaPzVGL4WxXI",
    authDomain: "ass2-39986.firebaseapp.com",
    projectId: "ass2-39986",
    storageBucket: "ass2-39986.firebasestorage.app",
    messagingSenderId: "1026097036332",
    appId: "1:1026097036332:web:2e43c666ce2c1777bc6589",
};

document.addEventListener("DOMContentLoaded", function() {
    // Safely initialize Firebase
    const app = initializeApp(firebaseConfig);
    const auth = getAuth(app);

    // Robust function to safely get an element
    function safeGetElement(id) {
        const element = document.getElementById(id);
        if (!element) {
            console.warn(`Element with id '${id}' not found`);
        }
        return element;
    }

    // Robust function to add event listener
    function safeAddEventListener(id, eventType, handler) {
        const element = safeGetElement(id);
        if (element) {
            element.addEventListener(eventType, handler);
        }
    }

    // Update UI function with fallback and logging
    function updateUI() {
        const cookie = document.cookie || '';
        const token = parseCookieToken(cookie);

        const loginBox = safeGetElement('loginDialog');
        const signOutButton = safeGetElement('sign-out');

        if (loginBox && signOutButton) {
            if (token && token.length > 0) {
                // User is logged in
                loginBox.style.display = 'none';
                signOutButton.style.display = 'block';
                
                // Update local storage to reflect authentication
                try {
                    const user = auth.currentUser;
                    if (user) {
                        localStorage.setItem('user', JSON.stringify({
                            email: user.email,
                            uid: user.uid
                        }));
                        // Trigger storage event to update UI
                        window.dispatchEvent(new Event('storage'));
                    }
                } catch (error) {
                    console.error('Error updating user info:', error);
                }
            } else {
                // User is not logged in
                loginBox.style.display = 'flex';
                signOutButton.style.display = 'none';
                
                // Clear local storage
                localStorage.removeItem('user');
                // Trigger storage event to update UI
                window.dispatchEvent(new Event('storage'));
            }
        }
    }

    // Parse cookie token with fallback
    function parseCookieToken(cookie) {
        if (!cookie) return "";
        
        const cookieParts = cookie.split(';')
            .map(part => part.trim())
            .filter(part => part.startsWith('token='));
        
        if (cookieParts.length > 0) {
            return cookieParts[0].split('=')[1] || "";
        }
        
        return "";
    }

    // Add event listeners with safety checks
    safeAddEventListener('sign-up', 'click', function() {
        const emailInput = safeGetElement('email');
        const passwordInput = safeGetElement('password');

        if (!emailInput || !passwordInput) {
            console.error('Email or password input not found');
            return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) {
            alert('Please enter both email and password');
            return;
        }

        createUserWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            console.log("User Created:", user);

            return user.getIdToken().then((token) => {
                document.cookie = `token=${token}; path=/; SameSite=Strict`;
                updateUI();
                window.location = "/";
            });
        })
        .catch((error) => {
            console.error("Signup Error:", error.code, error.message);
            alert(`Signup Error: ${error.message}`);
        });
    });

    safeAddEventListener('login', 'click', function() {
        const emailInput = safeGetElement('email');
        const passwordInput = safeGetElement('password');

        if (!emailInput || !passwordInput) {
            console.error('Email or password input not found');
            return;
        }

        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();

        if (!email || !password) {
            alert('Please enter both email and password');
            return;
        }

        signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            const user = userCredential.user;
            console.log("User Logged In:", user);

            return user.getIdToken().then((token) => {
                document.cookie = `token=${token}; path=/; SameSite=Strict`;
                updateUI();
                window.location = "/";
            });
        })
        .catch((error) => {
            console.error("Login Error:", error.code, error.message);
            alert(`Login Error: ${error.message}`);
        });
    });

    safeAddEventListener('sign-out', 'click', function() {
        signOut(auth)
        .then(() => {
            document.cookie = "token=; path=/; SameSite=Strict; expires=Thu, 01 Jan 1970 00:00:00 UTC"; 
            updateUI();
            window.location = "/";
        })
        .catch((error) => {
            console.error("Logout Error:", error.code, error.message);
            alert(`Logout Error: ${error.message}`);
        });
    });

    // Initial UI update
    updateUI();
});