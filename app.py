import os
import streamlit as st
import pandas as pd
import joblib

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Load the trained model
model_path = os.path.join(current_dir, 'lr.pkl')
model = joblib.load(model_path)

# Define a function to simulate authentication
def authenticate(email, password):
    try:
        # Read user credentials from a text file
        with open('user_credentials.txt', 'r') as file:
            credentials = [line.strip().split(',') for line in file.readlines()]
        
        # Check if the provided email and password match any of the credentials
        for credential in credentials:
            if len(credential) == 2:
                user_email, user_password = credential
                if email == user_email and password == user_password:
                    return True
        
        # If no matching credentials found, return False
        return False
    except Exception as e:
        print(f"An error occurred while authenticating: {e}")
        return False

def save_credentials(email, password):
    # Append new user credentials to the text file
    with open('user_credentials.txt', 'a') as file:
        file.write(f"{email},{password}\n")

def predict_production(county, area, precipitation, temperature, Fertilizer_KG):
    # Check if the county label is within the expected range
    expected_range = range(0, 23) 
    if county.isdigit() and int(county) in expected_range:
        # Convert county to integer for comparison
        county = int(county)
    else:
        # Handle the case of unseen label, perhaps by defaulting to a specific category
        county = 0 
        
    # Create a DataFrame with all input features
    data = pd.DataFrame({'County': [county], 'Area (HA)': [area], 'Precipitation (mm)': [precipitation],'Temperature(Celsius)': [temperature], 'Fertilizer(Kg)': [Fertilizer_KG]})
    
    # Make the prediction
    prediction = model.predict(data)
    return prediction[0]
def about_page():
    st.title('About')
    st.write("""
        <div style="font-size: 18px; line-height: 1.6;">
             <p></p>
            <p>Welcome to Future Yields, where innovation meets agriculture.</p>
             <p>Our platform utilizes cutting-edge machine learning algorithms to predict maize yields accurately. With real-time insights and personalized recommendations, we empower farmers to optimize crop management strategies for maximum productivity.</p>
            <p>Join us in shaping the future of agriculture with Future Yields.</p>
        </div>
    """, unsafe_allow_html=True)


def login_page():
    st.title('Login')

    # Create text input and password input with white text color
    email = st.text_input('Email', value='')
    password = st.text_input('Password', type='password', value='')
    sign_in_button = st.button('Sign In')
    if sign_in_button:
        if email.strip() == '' or password.strip() == '':
            st.error('Please enter both email and password.')
        else:
            if authenticate(email, password):
                st.session_state['logged_in'] = True
                st.success('Sign in successful! Kindly proceed to the prediction page')
                st.empty()
            else:
                st.error('Invalid email or password. Please try again.')

    if not st.session_state.get('logged_in'):  # Check if the user is not logged in
        # Sign up section
        st.markdown('---')  # Divider between login and sign up sections
        st.subheader('Don\'t have an account? Sign Up here')

        email_signup = st.text_input('Email (Sign Up)')
        password_signup = st.text_input('Password (Sign Up)', type='password')
        confirm_password_signup = st.text_input('Confirm Password (Sign Up)', type='password')

        if st.button('Sign Up'):
            if email_signup.strip() == '' or password_signup.strip() == '' or confirm_password_signup.strip() == '':
                st.error('Please fill in all the fields.')
            elif password_signup == confirm_password_signup:
                save_credentials(email_signup, password_signup)
                st.success('Sign up successful! You can now sign in.')
            else:
                st.error('Passwords do not match. Please try again.')

def prediction_page():
    if st.session_state.get('logged_in'):
        st.title('Happy Predicting')
        st.write('Enter the details to predict crop production:')
        county = st.selectbox('County', ['Baringo', 'Kisii', 'Siaya', 'UasinGishu', 'Bomet','Nakuru'])
        area = st.number_input('Area')
        precipitation = st.number_input('Precipitation')
        temperature = st.number_input('Temperature')
        Fertilizer_KG = st.number_input('Fertilizer(Kg)')
        
        if st.button('Predict'):
            production = predict_production(county, area, precipitation, temperature, Fertilizer_KG)
            st.success(f'The predicted maize production is  {production:.2f} (MT)')
    else:
        st.warning('You need to login to access this page.')

def logout_page():
    st.session_state['logged_in'] = False
    st.success('You have been logged out successfully.')
    # Set the selected page to "About"
    st.session_state.selected_page = "About"
    st.experimental_rerun()  # Rerun the app to navigate to about page

def main():
    st.set_page_config(layout="wide")

    st.markdown("<h1 style='text-align: center;'>Future Yields</h1>", unsafe_allow_html=True)
    st.image("https://www.harvestplus.org/wp-content/uploads/2021/08/Orange-maize-2.png",
              width=300,
              )

    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    # Initialize selected page
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = "About"

    # Pages navigation
    pages = {
        "About": about_page,
        "Login": login_page,
        "Prediction": prediction_page,
        "Logout": logout_page
    }

    selected_page = st.sidebar.radio("Navigation", list(pages.keys()), index=list(pages.keys()).index(st.session_state.selected_page))

    # Display selected page content
    pages[selected_page]()

if __name__ == '__main__':
    main()
