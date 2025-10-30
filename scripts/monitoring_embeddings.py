"""
Embeddings Usage Monitoring and Cost Tracking Utility

Monitors OpenAI embeddings API usage, calculates costs, and generates reports.
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import argparse
from collections import defaultdict
from tabulate import tabulate
from colorama import Fore, Style, init

# Constants
USAGE_LOG_FILE = "logs/embeddings_usage.jsonl"
PRICING = {
    "text-embedding-3-small": 0.00002,  # per 1K tokens
    "text-embedding-3-large": 0.00013
}


def read_usage_logs(log_file: str = USAGE_LOG_FILE) -> List[Dict]:
    """
    Načíta usage logs zo JSONL súboru.
    
    Args:
        log_file: Path to the JSONL log file
        
    Returns:
        List of usage record dictionaries
    """
    if not os.path.exists(log_file):
        return []
    
    records = []
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    # Convert timestamp string to datetime
                    if 'timestamp' in record:
                        record['timestamp'] = datetime.fromisoformat(
                            record['timestamp'].replace('Z', '+00:00')
                        )
                    records.append(record)
                except json.JSONDecodeError:
                    # Skip corrupt lines
                    continue
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []
    
    return records


def filter_by_period(records: List[Dict], period: str) -> List[Dict]:
    """
    Filtruje záznamy podľa obdobia (day/week/month/all).
    
    Args:
        records: List of usage records
        period: Time period filter (day/week/month/all)
        
    Returns:
        Filtered list of records
    """
    if period == "all":
        return records
    
    now = datetime.now()
    
    if period == "day":
        cutoff = now - timedelta(days=1)
    elif period == "week":
        cutoff = now - timedelta(days=7)
    elif period == "month":
        cutoff = now - timedelta(days=30)
    else:
        return records
    
    # Filter records where timestamp >= cutoff
    filtered = [r for r in records if r.get('timestamp', now) >= cutoff]
    return filtered


def calculate_stats(records: List[Dict]) -> Dict:
    """
    Vypočíta štatistiky z usage records.
    
    Args:
        records: List of usage records
        
    Returns:
        Dictionary with calculated statistics
    """
    if not records:
        return {
            "total_calls": 0,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "models_used": [],
            "period_start": None,
            "period_end": None,
            "duration_hours": 0.0,
            "avg_tokens_per_call": 0.0
        }
    
    total_calls = len(records)
    total_tokens = sum([r.get('tokens', 0) for r in records])
    models = set([r.get('model', 'unknown') for r in records])
    
    # Calculate estimated cost
    estimated_cost = 0.0
    for record in records:
        tokens = record.get('tokens', 0)
        model = record.get('model', '')
        cost_per_1k = PRICING.get(model, 0)
        estimated_cost += (tokens / 1000) * cost_per_1k
    
    # Get timestamps
    timestamps = [r.get('timestamp') for r in records if r.get('timestamp')]
    oldest = min(timestamps) if timestamps else None
    newest = max(timestamps) if timestamps else None
    
    # Calculate duration
    duration_hours = 0.0
    if oldest and newest:
        duration = newest - oldest
        duration_hours = duration.total_seconds() / 3600
    
    # Average tokens per call
    avg_tokens_per_call = total_tokens / total_calls if total_calls > 0 else 0.0
    
    return {
        "total_calls": total_calls,
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "models_used": list(models),
        "period_start": oldest,
        "period_end": newest,
        "duration_hours": duration_hours,
        "avg_tokens_per_call": avg_tokens_per_call
    }


def calculate_daily_stats(records: List[Dict]) -> Dict[str, Dict]:
    """
    Zoskupí usage podľa dní.
    
    Args:
        records: List of usage records
        
    Returns:
        Dictionary with daily statistics
    """
    daily_data = defaultdict(lambda: {"calls": 0, "tokens": 0, "cost": 0.0})
    
    for record in records:
        timestamp = record.get('timestamp')
        if not timestamp:
            continue
        
        date_key = timestamp.strftime('%Y-%m-%d')
        tokens = record.get('tokens', 0)
        model = record.get('model', '')
        cost_per_1k = PRICING.get(model, 0)
        cost = (tokens / 1000) * cost_per_1k
        
        daily_data[date_key]["calls"] += 1
        daily_data[date_key]["tokens"] += tokens
        daily_data[date_key]["cost"] += cost
    
    # Sort by date
    sorted_data = dict(sorted(daily_data.items()))
    return sorted_data


def print_summary_table(stats: Dict):
    """
    Vytlačí prehľadnú tabuľku štatistík.
    
    Args:
        stats: Statistics dictionary
    """
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{'EMBEDDINGS USAGE REPORT':^60}{Style.RESET_ALL}")
    print("=" * 60 + "\n")
    
    # Determine color based on cost
    cost = stats['estimated_cost_usd']
    if cost < 1:
        cost_color = Fore.GREEN
    elif cost < 10:
        cost_color = Fore.YELLOW
    else:
        cost_color = Fore.RED
    
    # Format period
    period_str = "N/A"
    if stats['period_start'] and stats['period_end']:
        period_str = f"{stats['period_start'].strftime('%Y-%m-%d %H:%M')} - {stats['period_end'].strftime('%Y-%m-%d %H:%M')}"
    
    table_data = [
        ["Total API Calls", f"{stats['total_calls']:,}"],
        ["Total Tokens", f"{stats['total_tokens']:,}"],
        ["Estimated Cost", f"{cost_color}${cost:.4f}{Style.RESET_ALL}"],
        ["Average per Call", f"{stats['avg_tokens_per_call']:.0f} tokens"],
        ["Models Used", ", ".join(stats['models_used']) if stats['models_used'] else "N/A"],
        ["Period", period_str],
        ["Duration", f"{stats['duration_hours']:.1f} hours"]
    ]
    
    print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="grid"))
    print()


def print_daily_breakdown(daily_stats: Dict):
    """
    Vytlačí denný breakdown.
    
    Args:
        daily_stats: Dictionary with daily statistics
    """
    if not daily_stats:
        return
    
    print(f"\n{Fore.CYAN}DAILY BREAKDOWN{Style.RESET_ALL}")
    print("-" * 60 + "\n")
    
    table_data = []
    total_calls = 0
    total_tokens = 0
    total_cost = 0.0
    
    for date, data in daily_stats.items():
        table_data.append([
            date,
            f"{data['calls']:,}",
            f"{data['tokens']:,}",
            f"${data['cost']:.4f}"
        ])
        total_calls += data['calls']
        total_tokens += data['tokens']
        total_cost += data['cost']
    
    # Add total row
    table_data.append([
        f"{Fore.CYAN}TOTAL{Style.RESET_ALL}",
        f"{Fore.CYAN}{total_calls:,}{Style.RESET_ALL}",
        f"{Fore.CYAN}{total_tokens:,}{Style.RESET_ALL}",
        f"{Fore.CYAN}${total_cost:.4f}{Style.RESET_ALL}"
    ])
    
    print(tabulate(table_data, headers=["Date", "Calls", "Tokens", "Cost ($)"], tablefmt="grid"))
    print()


def check_cost_alerts(stats: Dict, threshold_usd: float = 1.0) -> Optional[str]:
    """
    Skontroluje či náklady prekročili threshold.
    
    Args:
        stats: Statistics dictionary
        threshold_usd: Cost threshold in USD
        
    Returns:
        Warning message if threshold exceeded, None otherwise
    """
    cost = stats['estimated_cost_usd']
    if cost > threshold_usd:
        return f"⚠️  WARNING: Cost ${cost:.2f} exceeds threshold ${threshold_usd:.2f}"
    return None


def export_to_csv(records: List[Dict], output_file: str):
    """
    Exportuje usage data do CSV.
    
    Args:
        records: List of usage records
        output_file: Output CSV file path
    """
    import csv
    
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'model', 'tokens', 'cost', 'duration_ms'])
            
            for record in records:
                timestamp = record.get('timestamp', '')
                if isinstance(timestamp, datetime):
                    timestamp = timestamp.isoformat()
                
                model = record.get('model', '')
                tokens = record.get('tokens', 0)
                cost_per_1k = PRICING.get(model, 0)
                cost = (tokens / 1000) * cost_per_1k
                duration_ms = record.get('duration_ms', 0)
                
                writer.writerow([timestamp, model, tokens, f"{cost:.6f}", duration_ms])
        
        print(f"{Fore.GREEN}✓ Successfully exported {len(records)} records to {output_file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error exporting to CSV: {e}{Style.RESET_ALL}")


def generate_report(period: str = "day", alert_threshold: float = 1.0, export_csv: Optional[str] = None):
    """
    Hlavná funkcia pre generovanie reportu.
    
    Args:
        period: Time period for report (day/week/month/all)
        alert_threshold: Cost threshold for alerts in USD
        export_csv: Optional CSV export file path
    """
    # Load records
    records = read_usage_logs()
    
    if not records:
        print(f"{Fore.YELLOW}No usage data found in {USAGE_LOG_FILE}{Style.RESET_ALL}")
        return
    
    # Filter by period
    filtered_records = filter_by_period(records, period)
    
    if not filtered_records:
        print(f"{Fore.YELLOW}No usage data found for period: {period}{Style.RESET_ALL}")
        return
    
    # Calculate statistics
    stats = calculate_stats(filtered_records)
    daily_stats = calculate_daily_stats(filtered_records)
    
    # Print reports
    print_summary_table(stats)
    print_daily_breakdown(daily_stats)
    
    # Check alerts
    alert_msg = check_cost_alerts(stats, alert_threshold)
    if alert_msg:
        print(f"\n{Fore.RED}{alert_msg}{Style.RESET_ALL}\n")
    
    # Export to CSV if requested
    if export_csv:
        export_to_csv(filtered_records, export_csv)
    
    # Print recommendations
    print(f"\n{Fore.CYAN}RECOMMENDATIONS{Style.RESET_ALL}")
    print("-" * 60)
    
    avg_tokens = stats['avg_tokens_per_call']
    if avg_tokens > 5000:
        print(f"{Fore.YELLOW}• Consider chunking documents to reduce token usage per call{Style.RESET_ALL}")
    
    cost = stats['estimated_cost_usd']
    if cost > 10:
        print(f"{Fore.YELLOW}• High cost detected - review usage patterns and consider optimization{Style.RESET_ALL}")
    
    if 'text-embedding-3-large' in stats['models_used']:
        print(f"{Fore.YELLOW}• Consider using text-embedding-3-small for cost savings (6.5x cheaper){Style.RESET_ALL}")
    
    if stats['total_calls'] > 1000:
        print(f"{Fore.YELLOW}• Implement caching to reduce redundant API calls{Style.RESET_ALL}")
    
    print()


def main():
    """CLI entry point."""
    # Initialize colorama
    init(autoreset=True)
    
    # Argument parser
    parser = argparse.ArgumentParser(
        description="Monitor OpenAI embeddings usage and costs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --period day
  %(prog)s --period week --alert-threshold 5.0
  %(prog)s --export monthly_report.csv --period month
        """
    )
    
    parser.add_argument(
        '--period',
        choices=['day', 'week', 'month', 'all'],
        default='day',
        help='Time period for report (default: day)'
    )
    
    parser.add_argument(
        '--alert-threshold',
        type=float,
        default=1.0,
        help='Cost alert threshold in USD (default: 1.0)'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        metavar='CSV_FILE',
        help='Export usage data to CSV file'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Setup logging if verbose
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    try:
        generate_report(
            period=args.period,
            alert_threshold=args.alert_threshold,
            export_csv=args.export
        )
    except Exception as e:
        print(f"{Fore.RED}Error generating report: {e}{Style.RESET_ALL}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())