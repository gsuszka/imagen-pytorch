from asyncio.log import logger
from pathlib import Path
from functools import partial

import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms as T, utils
from typing import Optional


from PIL import Image

# helpers functions

def exists(val):
    return val is not None

def cycle(dl):
    while True:
        for data in dl:
            yield data

def convert_image_to(img_type, image):
    if image.mode != img_type:
        return image.convert(img_type)
    return image

def pil_loader(
    path: Path | str, 
    ignore_exception: bool = False, 
    remove_on_fail: bool = False,
) -> Optional[Image.Image]:
    logger.debug('Loading image from "%s"', path)

    try:
        with Image.open(path) as img:
            return img.convert("RGB")
    except Exception as e:
        logger.error('Couldn\'t load image from "%s"', path)

        if remove_on_fail:
            logger.warning('Removing "%s"', path)
            Path(path).unlink()

        if not ignore_exception:
            raise e

# dataset and dataloader

class Dataset(Dataset):
    def __init__(
        self,
        folder,
        image_size,
        exts = ['jpg', 'jpeg', 'png', 'tiff'],
        convert_image_to_type = None
    ):
        super().__init__()
        self.folder = folder
        self.image_size = image_size
        self.paths = [p for ext in exts for p in Path(f'{folder}').glob(f'**/*.{ext}')]

        convert_fn = partial(convert_image_to, convert_image_to_type) if exists(convert_image_to_type) else nn.Identity()

        self.transform = T.Compose([
            T.Lambda(convert_fn),
            T.Resize(image_size),
            T.RandomHorizontalFlip(),
            T.CenterCrop(image_size),
            T.ToTensor()
        ])

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, index):
        path = self.paths[index]
        img = pil_loader(path)
        return self.transform(img)

def get_images_dataloader(
    folder,
    *,
    batch_size,
    image_size,
    shuffle = True,
    cycle_dl = False,
    pin_memory = True
):
    ds = Dataset(folder, image_size)
    dl = DataLoader(ds, batch_size = batch_size, shuffle = shuffle, pin_memory = pin_memory)

    if cycle_dl:
        dl = cycle(dl)
    return dl
