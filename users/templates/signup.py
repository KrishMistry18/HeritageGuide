{% comment %} import streamlit as st

st.set_page_config(
    page_title="Sign-Up Page",
    layout="wide",  
    initial_sidebar_state="collapsed"
) {% endcomment %}

st.markdown("""
    <style>
    .container {
        background-color: #e74c3c;
        border-radius: 30px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        width: 400px;
        height: 500px;
        padding: 40px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: auto;
        margin-top: 40px;
        text-align: center;
    }
    
    .signup-title {
        color: white;
        font-size: 25px;
        margin-top: -1px;
        margin-bottom: 20px;
    }
            
    .input-field {
        width: 100%;
        height: 40px;
        margin: 10px 0;
        background-color: #2d3545;
        border: none;
        border-radius: 5px;
        color: white;
        font-size: 16px;
        text-align: center;
        box-sizing: border-box;
        padding: 10px;
    }

    .input-field::placeholder {
        color: #8391a7;
        opacity: 0.7;
    }
    
    .signup-button {
        width: 100%;
        height: 40px;
        margin-top: 15px;
        background-color: #1abc9c;
        border: none;
        border-radius: 5px;
        color: white;
        font-size: 18px;
        cursor: pointer;
    }
    
    .signup-button:hover {
        background-color: #16a085;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="container">
        <h2 class="signup-title">New Account</h2>
        {% csrf_token%}
        {{signupform.as_p}}
        <input type="text" class="input-field" placeholder="Enter your username">
        <input type="password" class="input-field" placeholder="Enter your password">
        <button class="signup-button">Sign-Up</button>
        {% load socialaccount %}
        <h2>Google Login</h2>
        <a href="{% provider_login_url 'google' %}?next=/">signup With Google</a>
        {% if user.is_authenticated %}
        <p>You are signed in as {{ user.email }}</p>
        <a href="logout">Logout</a>
    {% endif %}
    

        
    </div>
""", unsafe_allow_html=True)
