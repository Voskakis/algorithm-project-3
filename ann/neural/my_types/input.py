import argparse
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ann.neural.enums import EndianType
from ann.neural.enums.kahip_modes import KahipMode


def parse_bool(x: str) -> bool:
    return x.lower() in ("1", "true", "yes", "y")


import struct


def load_idx_images(path):
    with open(path, "rb") as f:
        magic, num_images, rows, cols = struct.unpack(">IIII", f.read(16))
        image_size = rows * cols
        data = f.read(num_images * image_size)
    images = [list(data[i * image_size:(i + 1) * image_size]) for i in range(num_images)]
    return images


def load_sift_descriptors(path):
    descriptors = []
    with open(path, "rb") as f:
        while True:
            dim_bytes = f.read(4)
            if not dim_bytes:
                break
            (dim,) = struct.unpack("<I", dim_bytes)  # little-endian
            vec = f.read(dim)
            if len(vec) != dim:
                raise ValueError("Truncated file")
            descriptors.append(list(vec))
    return descriptors


@dataclass
class BuildInput:
    input_file: Path
    index_path: Path
    type: EndianType
    knn_neighbors: Optional[int] = 10
    members: Optional[int] = 100
    imbalance: Optional[float] = 0.03
    kahip_mode: Optional[KahipMode] = 2
    layers: Optional[int] = 3
    nodes: Optional[int] = 64
    epochs: Optional[int] = 10
    batch_size: Optional[int] = 128
    learn_rate: Optional[float] = 0.001
    seed: Optional[int] = 1
    input_data = []

    def get_initial(self):
        if self.type == EndianType.Sift:
            return load_sift_descriptors(self.input_file)
        else:
            return load_idx_images(self.input_file)

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", dest="input_file", type=Path, required=True)
        parser.add_argument("-i", dest="index_path", type=Path, required=True)
        parser.add_argument("-type", dest="type", choices=[e for e in EndianType], required=True, type=EndianType)
        parser.add_argument("--knn", dest="knn_neighbors", type=int, default=10)
        parser.add_argument("-m", dest="members", type=int, default=100)
        parser.add_argument("--layers", type=int, default=3)
        parser.add_argument("--imbalance", type=float, default=0.03)
        parser.add_argument("--kahip_mode", type=lambda x: KahipMode(int(x)),
            choices=[KahipMode.FAST, KahipMode.ECO, KahipMode.STRONG], default=KahipMode.STRONG)
        parser.add_argument("--nodes", type=int, default=64)
        parser.add_argument("--epochs", type=int, default=10)
        parser.add_argument("--batch_size", type=int, default=128)
        parser.add_argument("--lr", dest="learn_rate", type=float, default=0.001)
        parser.add_argument("--seed", type=int, default=1)
        build_input = BuildInput(**vars(parser.parse_args()))
        output_path = f"{uuid.uuid4()}"

        if build_input.type == EndianType.Sift:
            build_input.input_data = load_sift_descriptors(build_input.input_file)
        else:
            build_input.input_data = load_idx_images(build_input.input_file)
        with open(output_path, "w") as f:
            for vec in build_input.input_data:
                line = " ".join(map(str, vec))
                f.write(line + "\n")
        build_input.input_file = Path(output_path)
        return build_input


@dataclass
class SearchInput:
    input_file: Path
    query_file: Path
    index_path: Path
    output_file: Path
    type: EndianType
    layers: Optional[int] = 3
    members: Optional[int] = 100
    nodes: Optional[int] = 64
    nearest_neighbors: Optional[int] = 1
    search_radius: Optional[float] = 2000
    bins_check: Optional[int] = 5
    range: Optional[bool] = True
    input_data = []
    query_data = []

    @classmethod
    def parse_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("-d", required=True, type=Path, dest="input_file")
        parser.add_argument("-q", required=True, type=Path, dest="query_file")
        parser.add_argument("-i", required=True, type=Path, dest="index_path")
        parser.add_argument("-o", required=True, type=Path, dest="output_file")
        parser.add_argument("-type", required=True, choices=["sift", "mnist"])
        parser.add_argument("-N", type=int, default=1, dest="nearest_neighbors")
        parser.add_argument("-R", type=float, dest="search_radius")
        parser.add_argument("-T", type=int, default=5, dest="bins_check")
        parser.add_argument("-range", type=parse_bool, default=True, dest="range")
        parser.add_argument("-m", dest="members", type=int, default=100)
        parser.add_argument("--layers", type=int, default=3, dest="layers")
        parser.add_argument("--nodes", type=int, default=64, dest="nodes")
        args = parser.parse_args()
        endian_type = EndianType(args.type)
        if not range:
            args.search_radius = 0
        if args.search_radius is None:
            if endian_type == EndianType.Sift:
                args.search_radius = 2800
            else:
                args.search_radius = 2000
        search_input = SearchInput(input_file=args.input_file, query_file=args.query_file, index_path=args.index_path,
            output_file=args.output_file, type=endian_type, nearest_neighbors=args.nearest_neighbors,
            search_radius=args.search_radius, bins_check=args.bins_check, range=args.range, layers=args.layers, members=args.members, nodes=args.nodes)
        if search_input.type == EndianType.Sift:
            search_input.input_data = load_sift_descriptors(search_input.input_file)
        else:
            search_input.input_data = load_idx_images(search_input.input_file)
        if search_input.type == EndianType.Sift:
            search_input.query_data = load_sift_descriptors(search_input.query_file)
        else:
            search_input.query_data = load_idx_images(search_input.query_file)
        return search_input
