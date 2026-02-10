# OQR Encoder/Decoder


## Prerequisites

- **Python 3.8 or higher**
- **pip** (Python package manager)
- **Virtual Environment** (recommended)

### System Requirements
- **RAM**: Minimum 2GB
- **Disk Space**: 500MB for dependencies
- **OS**: Linux, macOS, or Windows

---

## Installation



### Create Virtual Environment (Recommended)

**On Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verify Installation

```bash
python3 -c "from encoder import encode; print('Installation successful!')"
```

---

## Quick Start

### Web Interface (Recommended)

1. **Start the Flask server:**
   ```bash
   python3 app.py
   ```

2. **Open your browser:**
   - Navigate to `http://localhost:5000`
   - Default port: **5000**

3. **Encode a QR Code:**
   - Click "Encoder" tab
   - Enter a name for your QR code
   - Select Type (2 or 3)
   - Enter your data values
   - Choose output format
   - Click "Generate"

4. **Decode a QR Code:**
   - Click "Decoder" tab
   - Upload your image file
   - View decoded values

## Usage

### Web Interface

#### Encoder

1. **Navigate to** `/encoder`
2. **Fill in the form:**
   - **Name**: Identifier for your QR code (e.g., "invoice_001")
   - **Type**: Select "2" or "3" based on your needs
   - **Data Fields**: Enter your data values
   - **Format**: Choose output image format
3. **Click "Generate"**
4. **Download or view** the generated QR code

#### Decoder

1. **Navigate to** `/decoder`
2. **Upload** an image file (PNG, JPEG, BMP, TIFF, WebP)
3. **View** the decoded values:
   - **Success**: Shows all detected values (Value 1, Value 2, Value 3)
   - **Error**: Shows "NO OQR DETECTED - Try Again" message with suggestions

**Error Handling:**
- If QR codes cannot be detected, a clear error message is displayed
- User is instructed to upload a clearer image
- Automatic fallback to sibling QR files if available
- Detailed console logs available in debug mode