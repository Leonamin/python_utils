from PIL import Image  # install by > python3 -m pip install --upgrade Pillow  # ref. https://pillow.readthedocs.io/en/latest/installation.html#basic-installation

images = [
    Image.open("/Users/apple/Desktop/" + f)
    for f in ["nh.png"]
]

pdf_path = "./nh.pdf"

images[0].save(
    pdf_path, "PDF", resolution=100.0, save_all=True, append_images=images[1:]
)
