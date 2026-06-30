"""Generate placeholder images for products."""
import os
from PIL import Image, ImageDraw, ImageFont

def create_placeholder_image(width, height, category, name, filepath):
    """Create a placeholder image with category info."""
    # Color scheme for categories
    colors = {
        'electronics': {'bg': '#1e40af', 'accent': '#60a5fa'},
        'fashion': {'bg': '#be185d', 'accent': '#f472b6'},
        'home': {'bg': '#7c2d12', 'accent': '#fb923c'},
        'sports': {'bg': '#166534', 'accent': '#86efac'},
        'perfumes': {'bg': '#5b21b6', 'accent': '#d8b4fe'},
        'placeholder': {'bg': '#4b5563', 'accent': '#9ca3af'},
    }
    
    cat_lower = category.lower()
    color_set = colors.get(cat_lower, colors['placeholder'])
    bg_color = color_set['bg']
    accent_color = color_set['accent']
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw accent bar
    draw.rectangle([0, 0, width, 30], fill=accent_color)
    
    # Draw center decoration
    center_x, center_y = width // 2, height // 2
    radius = 50
    draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius],
                 outline=accent_color, width=3)
    
    # Draw category text
    try:
        # Try to use a nice font, fallback to default
        font_size = 24
        font_small = ImageFont.load_default()
    except:
        font_small = ImageFont.load_default()
    
    # Draw category at top
    draw.text((20, 8), category.upper(), fill='white', font=font_small)
    
    # Draw product name (truncated to fit)
    product_name = name[:25] + "..." if len(name) > 25 else name
    draw.text((center_x - 80, center_y - 10), product_name, fill='white', font=font_small)
    
    # Save image
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)
    return filepath


# Product data mapping
products = {
    'electronics': [
        'Pro Wireless Headphones',
        'Ultra Smart Watch Pro',
        'Portable Bluetooth Speaker',
        '4K Webcam Pro',
        'Wireless Charging Dock',
        'Noise-Cancelling Earbuds',
        'Mechanical Gaming Keyboard',
        'USB-C Hub Adapter',
    ],
    'fashion': [
        'Classic Leather Jacket',
        'Designer Sunglasses',
        'Premium Canvas Sneakers',
        'Minimalist Leather Watch',
        'Wool Blend Overcoat',
        'Leather Crossbody Bag',
        'Cashmere Blend Scarf',
    ],
    'home': [
        'Aromatherapy Diffuser',
        'Cozy Throw Blanket',
        'Ceramic Plant Pot Set',
        'Smart LED Desk Lamp',
        'Scented Candle Collection',
        'Bamboo Serving Tray',
    ],
    'sports': [
        'Performance Running Shoes',
        'Yoga Mat Premium',
        'Insulated Water Bottle',
        'Resistance Bands Set',
        'Adjustable Dumbbells Set',
        'Sports Gym Bag',
    ],
    'perfumes': [
        'Midnight Rose Eau de Parfum',
        'Ocean Breeze Cologne',
        'Velvet Oud Intense',
        'Citrus Garden EDT',
        'Golden Amber Perfume',
        'Wild Lavender Mist',
    ],
}

# Create images
base_path = 'd:\\Data Science Projects\\Flask\\static\\images'
created_count = 0

for category, product_names in products.items():
    for idx, product_name in enumerate(product_names):
        filename = f"{product_name.lower().replace(' ', '_')}.png"
        filepath = os.path.join(base_path, category, filename)
        create_placeholder_image(400, 400, category, product_name, filepath)
        created_count += 1
        print(f"✅ Created: {filepath}")

print(f"\n✅ Successfully created {created_count} placeholder images!")
