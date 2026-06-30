#!/usr/bin/env python3
"""Plot mean-force curves from one or more mean_force_table.csv files."""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Sequence


def parse_curve(spec: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for item in spec.split(','):
        item = item.strip()
        if not item:
            continue
        if '=' not in item:
            raise ValueError(f"Curve item lacks '=': {item}")
        key, value = item.split('=', 1)
        data[key.strip()] = value.strip()
    if 'file' not in data:
        raise ValueError("Each --curve must include file=...")
    if 'dataset' not in data:
        raise ValueError("Each --curve must include dataset=...")
    data.setdefault('label', data['dataset'])
    data.setdefault('rc_index', '0')
    return data


def read_rows(curve: dict[str, str], y_column: str) -> list[dict[str, str]]:
    with Path(curve['file']).open('r', newline='', encoding='utf-8') as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{curve['file']} has no CSV header")
        required = ['dataset_label', 'rc_index', 'reaction_coordinate_au', y_column]
        missing = [col for col in required if col not in reader.fieldnames]
        if missing:
            raise ValueError(f"{curve['file']} missing columns: {missing}")
        return [row for row in reader if row['dataset_label'] == curve['dataset'] and int(row['rc_index']) == int(curve['rc_index'])]


def order_rows(rows: list[dict[str, str]], order: str) -> list[dict[str, str]]:
    if order == 'ascending':
        return sorted(rows, key=lambda row: float(row['reaction_coordinate_au']))
    if order == 'descending':
        return sorted(rows, key=lambda row: float(row['reaction_coordinate_au']), reverse=True)
    if order == 'input':
        return list(rows)
    raise ValueError(order)


def plot_curves(args: argparse.Namespace, y_column: str, default_ylabel: str) -> int:
    if not args.confirm_parameters:
        print('Refusing to plot until --confirm-parameters is supplied.', file=sys.stderr)
        print('Confirm initial-to-final RC order, units, selected datasets, and visual styles.', file=sys.stderr)
        return 2
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(args.width, args.height), dpi=args.dpi)
    for spec in args.curve:
        curve = parse_curve(spec)
        rows = order_rows(read_rows(curve, y_column), args.rc_order)
        if not rows:
            raise ValueError(f"No rows matched curve spec: {spec}")
        x = [float(row['reaction_coordinate_au']) for row in rows]
        y = [float(row[y_column]) for row in rows]
        style = {
            'label': curve.get('label', curve['dataset']),
            'color': curve.get('color'),
            'linestyle': curve.get('linestyle', '-'),
            'marker': curve.get('marker', None),
            'linewidth': float(curve.get('linewidth', args.linewidth)),
            'markersize': float(curve.get('markersize', args.markersize)),
        }
        style = {k: v for k, v in style.items() if v is not None and v != 'none'}
        ax.plot(x, y, **style)
    ax.set_xlabel(args.xlabel)
    ax.set_ylabel(args.ylabel or default_ylabel)
    if args.title:
        ax.set_title(args.title)
    if args.xlim:
        ax.set_xlim(args.xlim[0], args.xlim[1])
    if args.ylim:
        ax.set_ylim(args.ylim[0], args.ylim[1])
    if args.grid:
        ax.grid(True, alpha=0.3)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(args.output)
    print(f"Saved plot to {args.output}")
    print(f"RC order used for every curve: {args.rc_order}. Keep this consistent with integration/TST state convention.")
    return 0


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument('--curve', action='append', required=True, help='Curve spec: file=...,dataset=...,label=...,rc_index=0,color=...,linestyle=...,marker=...')
    parser.add_argument('--output', required=True, help='Output image path, e.g. mean_force.png.')
    parser.add_argument('--rc-order', choices=['ascending', 'descending', 'input'], default='ascending', help='Plot from initial to final. Default ascending small RC -> large RC; use descending when large RC is initial.')
    parser.add_argument('--xlabel', default='Reaction coordinate (au)', help='X-axis label.')
    parser.add_argument('--ylabel', default='', help='Y-axis label override.')
    parser.add_argument('--title', default='', help='Plot title.')
    parser.add_argument('--xlim', nargs=2, type=float, default=None, help='X-axis limits.')
    parser.add_argument('--ylim', nargs=2, type=float, default=None, help='Y-axis limits.')
    parser.add_argument('--width', type=float, default=6.0, help='Figure width in inches.')
    parser.add_argument('--height', type=float, default=4.0, help='Figure height in inches.')
    parser.add_argument('--dpi', type=int, default=300, help='Figure DPI.')
    parser.add_argument('--linewidth', type=float, default=2.0, help='Default line width.')
    parser.add_argument('--markersize', type=float, default=5.0, help='Default marker size.')
    parser.add_argument('--grid', action='store_true', help='Show grid.')
    parser.add_argument('--confirm-parameters', action='store_true', help='Required confirmation of initial/final direction, units, datasets, and styles.')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Plot MeanForce versus reaction coordinate from one or more mean_force_table.csv files.')
    add_common_args(parser)
    parser.add_argument('--y-column', default='mean_force_au', help='Mean-force column to plot. Default: mean_force_au.')
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return plot_curves(args, args.y_column, 'Mean force (au)')


if __name__ == '__main__':
    raise SystemExit(main())
