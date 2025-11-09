import streamlit as st
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image
import io

# --- CONFIGURATION ---
st.set_page_config(page_title="Safe QR Tool", page_icon="🔒", layout="centered")

# 🔑 ADMIN PASSWORD (Change this!)
# For real apps, use st.secrets instead of hardcoding.
ADMIN_PASSWORD = "admin123"

# --- SESSION STATE SETUP ---
# This remembers your login status while you use the app.
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False

# --- HELPER FUNCTIONS ---
def generate_qr(data):
    """Generates QR code as a PIL image."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")

def scan_qr(image_file):
    """Decodes QR code from an uploaded image."""
    img = Image.open(image_file)
    decoded_objects = decode(img)
    # Return a list of all decoded text found in the image
    return [obj.data.decode("utf-8") for obj in decoded_objects], img

# =========================================
# SIDEBAR NAVIGATION
# =========================================
st.sidebar.header("Navigation")

# Define menu based on login status
if st.session_state['is_admin']:
    menu_options = ["📏 Scan QR (Public)", "🔑 Generate QR (Admin)", "🚪 Logout"]
else:
    menu_options = ["📏 Scan QR (Public)", "🔒 Admin Login"]

choice = st.sidebar.radio("Go to:", menu_options)

st.sidebar.divider()
st.sidebar.info("Only admins can generate new codes.")

# =========================================
# PAGE 1: SCAN QR (PUBLIC)
# =========================================
if "Scan QR" in choice:
    st.title("📏 Product Scanner")
    st.write("Upload an image to check a product QR code.")

    uploaded_file = st.file_uploader("Choose a QR image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        # Perform scan
        results, img = scan_qr(uploaded_file)
        
        # Show results
        col1, col2 = st.columns(2)
        with col1:
            st.image(img, caption="Your Image", use_container_width=True)
        with col2:
            if results:
                st.success("✅ QR Code Detected!")
                for result in results:
                    st.code(result, language="text")
            else:
                st.error("❌ No valid QR code found.")

# =========================================
# PAGE 2: ADMIN LOGIN
# =========================================
elif choice == "🔒 Admin Login":
    st.title("🔒 Admin Access")
    
    with st.form("login_form"):
        password_attempt = st.text_input("Enter Admin Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if password_attempt == ADMIN_PASSWORD:
                st.session_state['is_admin'] = True
                st.success("Login successful! Reloading...")
                st.rerun() # Reloads app to update the menu immediately
            else:
                st.error("Incorrect password.")

# =========================================
# PAGE 3: GENERATE QR (PRIVATE)
# =========================================
elif "Generate QR" in choice:
    # Double-check security in case they tried to bypass the menu
    if not st.session_state['is_admin']:
        st.warning("⛔ Authorized access only.")
        st.stop()

    st.title("🔑 QR Generator")
    st.write("Create official product QR codes.")
    
    qr_text = st.text_input("Enter Product URL or ID", placeholder="https://mysite.com/product/123")
    
    if st.button("Create QR Code"):
        if qr_text.strip():
            qr_img = generate_qr(qr_text)
            
            # Convert for display/download
            buf = io.BytesIO()
            qr_img.save(buf, format="PNG")
            byte_im = buf.getvalue()
            
            st.image(byte_im, width=250, caption="Preview")
            st.download_button(
                label="💾 Download PNG",
                data=byte_im,
                file_name="product_qr.png",
                mime="image/png"
            )
        else:
            st.warning("Please enter some text first.")

# =========================================
# LOGOUT ACTION
# =========================================
elif choice == "🚪 Logout":
    st.session_state['is_admin'] = False
    st.rerun()