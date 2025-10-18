#ADD CSS STYLES WITH TROPICAL LEAVES ANIMATION
def setUp_CSS(st):
    st.markdown("""
        <style>
            /* --- Correct Placeholder Styling for Chat Input --- */
            /* Light Mode */
            .stChatInput input::placeholder,
            .stChatInput div[data-baseweb="input"] input::placeholder {
                color: rgba(120, 120, 120, 0.7) !important;
            }

            /* Dark Mode */
            [data-theme="dark"] .stChatInput input::placeholder,
            [data-theme="dark"] .stChatInput div[data-baseweb="input"] input::placeholder {
                color: rgba(200, 200, 200, 0.5) !important;
            }

            /* Optional: Adjust input text color too */
            .stChatInput input {
                color: rgba(0, 0, 0, 0.85) !important;
            }
            [data-theme="dark"] .stChatInput input {
                color: rgba(255, 255, 255, 0.9) !important;
            }

            /* Center Text Class */  
            .center-text { text-align: center; }
                
            /* Circular Image Styling for Welcome Logo */
            .logo-container img {
                border-radius: 50%;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                width: 250px !important;
                height: 250px !important;
                object-fit: cover;
                display: block;
                margin: 0 auto;
            }
            
            /* Center entire welcome section vertically and horizontally */
            .welcome-container {
                display: flex;
                flex-direction: column;
                align-items: center;       /* horizontal centering */
                justify-content: center;   /* vertical centering */
                text-align: center;
                width: 100%;
                margin: 0 auto;
            }

            /* Style text for better visual hierarchy - Auto adapting */
            .welcome-container h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                color: var(--text-color) !important;  /* Uses Streamlit's theme color */
            }

            .welcome-container p {
                font-size: 1.2rem;
                color: var(--text-color) !important;  /* Uses Streamlit's theme color */
                margin-top: 0;
            }
                
            .quick-start-title {
                text-align: center;
                margin-top: 2rem;
                margin-bottom: 1rem;
                font-weight: 600;
            }

            /* ========================================= */
            /* TROPICAL LEAVES ANIMATION FOR CHAT INPUT */
            /* ========================================= */
            
            /* Container wrapper for the chat input with leaves */
            .stChatInput {
                position: relative;
                transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            /* Scale up the entire chat input on hover/focus */
            .stChatInput:hover {
                transform: scale(1.02);
            }

            .stChatInput:focus-within {
                transform: scale(1.03);
            }

            /* Create tropical leaf elements using pseudo-elements */
            .stChatInput::before,
            .stChatInput::after {
                content: '🌿';
                position: absolute;
                font-size: 2rem;
                opacity: 0;
                transition: all 0.8s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                z-index: -1; /* Keep leaves behind to avoid interfering */
            }

            /* Left leaf - positioned safely away from text box */
            .stChatInput::before {
                left: -45px;
                top: 50%;
                transform: translateY(-50%) rotate(-45deg) scale(0.5);
            }

            /* Right leaf - positioned safely away from text box */
            .stChatInput::after {
                right: -45px;
                top: 50%;
                transform: translateY(-50%) rotate(45deg) scale(0.5);
            }

            /* Animate leaves on hover */
            .stChatInput:hover::before {
                opacity: 0.8;
                left: -35px;
                transform: translateY(-50%) rotate(-25deg) scale(1);
            }

            .stChatInput:hover::after {
                opacity: 0.8;
                right: -35px;
                transform: translateY(-50%) rotate(25deg) scale(1);
            }

            /* Animate leaves when input is focused */
            .stChatInput:focus-within::before {
                opacity: 1;
                left: -30px;
                transform: translateY(-50%) rotate(-15deg) scale(1.1);
                animation: leafSway 3s ease-in-out infinite;
            }

            .stChatInput:focus-within::after {
                opacity: 1;
                right: -30px;
                transform: translateY(-50%) rotate(15deg) scale(1.1);
                animation: leafSway 3s ease-in-out infinite reverse;
            }

            /* Gentle swaying animation */
            @keyframes leafSway {
                0%, 100% {
                    transform: translateY(-50%) rotate(-15deg) scale(1.1);
                }
                50% {
                    transform: translateY(-55%) rotate(-10deg) scale(1.15);
                }
            }

            /* Add a subtle glow effect to the input on focus */
            .stChatInput:focus-within input {
                box-shadow: 0 0 0 2px rgba(52, 211, 153, 0.3),
                            0 0 20px rgba(52, 211, 153, 0.1) !important;
                transition: box-shadow 0.3s ease;
            }

            /* Enhance the tropical vibe with additional leaf decorations */
            .stChatInput:focus-within input {
                background: linear-gradient(
                    to right,
                    rgba(52, 211, 153, 0.02),
                    transparent 20%,
                    transparent 80%,
                    rgba(52, 211, 153, 0.02)
                ) !important;
            }

            /* Smooth transition for the input border */
            .stChatInput input {
                transition: all 0.3s ease !important;
            }

            /* Remove red border on hover/focus - target all possible selectors */
            .stChatInput:hover input,
            .stChatInput input:hover,
            .stChatInput input:focus,
            .stChatInput:focus-within input,
            .stChatInput textarea:hover,
            .stChatInput textarea:focus,
            .stChatInput div[data-baseweb="input"]:hover,
            .stChatInput div[data-baseweb="input"]:focus-within {
                border-color: rgba(52, 211, 153, 0.3) !important;
                outline: none !important;
            }

            /* Target the actual input wrapper */
            .stChatInput > div:hover,
            .stChatInput > div:focus-within {
                border-color: rgba(52, 211, 153, 0.3) !important;
            }

                        /* Dark mode border adjustments */
            [data-theme="dark"] .stChatInput:hover input,
            [data-theme="dark"] .stChatInput input:hover,
            [data-theme="dark"] .stChatInput input:focus,
            [data-theme="dark"] .stChatInput:focus-within input,
            [data-theme="dark"] .stChatInput textarea:hover,
            [data-theme="dark"] .stChatInput textarea:focus,
            [data-theme="dark"] .stChatInput div[data-baseweb="input"]:hover,
            [data-theme="dark"] .stChatInput div[data-baseweb="input"]:focus-within,
            [data-theme="dark"] .stChatInput > div:hover,
            [data-theme="dark"] .stChatInput > div:focus-within {
                border-color: rgba(52, 211, 153, 0.4) !important;
                outline: none !important;
            }

            /* ========================================= */
            /* ANIMATED SIDEBAR TOGGLE ARROW */
            /* ========================================= */
            
            /* Target the sidebar collapse/expand button - try multiple selectors */
            button[kind="header"],
            button[data-testid="collapsedControl"],
            [data-testid="collapsedControl"],
            [data-testid="stSidebarCollapsedControl"],
            section[data-testid="stSidebar"] > button,
            .css-1544g2n,
            div[data-testid="collapsedControl"] button,
            button[aria-label*="sidebar"] {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                transform-origin: center !important;
            }

            /* Hover effect - slide right and grow */
            button[kind="header"]:hover,
            button[data-testid="collapsedControl"]:hover,
            [data-testid="collapsedControl"]:hover,
            [data-testid="stSidebarCollapsedControl"]:hover,
            section[data-testid="stSidebar"] > button:hover,
            .css-1544g2n:hover,
            div[data-testid="collapsedControl"] button:hover,
            button[aria-label*="sidebar"]:hover {
                transform: translateX(8px) scale(1.15) !important;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            }

            /* Active/click effect - keep it functional */
            button[kind="header"]:active,
            button[data-testid="collapsedControl"]:active,
            [data-testid="collapsedControl"]:active,
            [data-testid="stSidebarCollapsedControl"]:active,
            section[data-testid="stSidebar"] > button:active,
            .css-1544g2n:active,
            div[data-testid="collapsedControl"] button:active,
            button[aria-label*="sidebar"]:active {
                transform: translateX(8px) scale(1.1) !important;
            }
        

            /* Dark mode adjustments for leaves */
            [data-theme="dark"] .stChatInput:focus-within input {
                box-shadow: 0 0 0 2px rgba(52, 211, 153, 0.4),
                            0 0 25px rgba(52, 211, 153, 0.15) !important;
            }

            /* ========================================= */
            /* ANIMATED SIDEBAR TOGGLE ARROW */
            /* ========================================= */
            
            /* Target all possible sidebar toggle button selectors */
            [data-testid="stSidebarNav"] + div button,
            [data-testid="collapsedControl"],
            section[data-testid="stSidebar"] ~ button,
            div[data-testid="stSidebarUserContent"] button:first-child,
            button[kind="header"],
            .stApp > header button,
            button[aria-label="Open sidebar navigation"],
            button[aria-label="Close sidebar navigation"] {
                transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                transform-origin: center center !important;
            }

            /* Hover effect - slide right and grow */
            [data-testid="stSidebarNav"] + div button:hover,
            [data-testid="collapsedControl"]:hover,
            section[data-testid="stSidebar"] ~ button:hover,
            div[data-testid="stSidebarUserContent"] button:first-child:hover,
            button[kind="header"]:hover,
            .stApp > header button:hover,
            button[aria-label="Open sidebar navigation"]:hover,
            button[aria-label="Close sidebar navigation"]:hover {
                transform: translateX(10px) scale(1.2) !important;
            }

            /* Active/click state */
            [data-testid="stSidebarNav"] + div button:active,
            [data-testid="collapsedControl"]:active,
            section[data-testid="stSidebar"] ~ button:active,
            div[data-testid="stSidebarUserContent"] button:first-child:active,
            button[kind="header"]:active,
            .stApp > header button:active,
            button[aria-label="Open sidebar navigation"]:active,
            button[aria-label="Close sidebar navigation"]:active {
                transform: translateX(10px) scale(1.15) !important;
            }

            /* More aggressive targeting - catch any button in the top left */
            .stApp > div > div > div > button:first-of-type,
            header button:first-of-type {
                transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
                transform-origin: center center !important;
            }

            .stApp > div > div > div > button:first-of-type:hover,
            header button:first-of-type:hover {
                transform: translateX(10px) scale(1.2) !important;
            }

            .stApp > div > div > div > button:first-of-type:active,
            header button:first-of-type:active {
                transform: translateX(10px) scale(1.15) !important;
            }
        </style>
        """, unsafe_allow_html=True)