#!/usr/bin/env python3
"""
Database Performance Comparison Tool

Compares performance results between Docker SQL Server, Microsoft Fabric SQL,
and Azure SQL Database (Serverless) to determine the source of latency issues.

Features:
- Load and compare JSON performance results
- Statistical analysis and visualization
- Performance recommendations
- Latency source identification

Usage:
    python compare_database_performance.py
"""

import os
import json
import glob
import statistics
from datetime import datetime
from pathlib import Path

class DatabasePerformanceComparator:
    def __init__(self):
        self.results_dir = Path(__file__).parent.parent / "tests" / "results"
        self.comparisons = {}
        
    def load_results(self):
        """Load all available performance test results"""
        print("📊 Loading Performance Test Results...")
        print("-" * 50)
        
        # Look for result files
        result_files = {
            'docker': glob.glob(str(self.results_dir / "*docker*.json")),
            'fabric': glob.glob(str(self.results_dir / "*fabric*.json")),
            'azure_sql': glob.glob(str(self.results_dir / "*azure_sql*.json"))
        }
        
        loaded_results = {}
        
        for db_type, files in result_files.items():
            if files:
                # Use the most recent file
                latest_file = max(files, key=os.path.getctime)
                try:
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                        loaded_results[db_type] = data
                        print(f"✅ {db_type.upper()}: {os.path.basename(latest_file)}")
                except Exception as e:
                    print(f"❌ Failed to load {db_type}: {e}")
            else:
                print(f"⚠️  {db_type.upper()}: No results found")
        
        return loaded_results
    
    def extract_key_metrics(self, results):
        """Extract key performance metrics from results"""
        metrics = {}
        
        for db_type, data in results.items():
            metrics[db_type] = {
                'connection_avg': None,
                'orm_avg': None,
                'sql_avg': None,
                'cold_start': None,
                'warm_query': None
            }
            
            # Connection performance
            if 'connection_tests' in data and data['connection_tests']:
                metrics[db_type]['connection_avg'] = data['connection_tests'].get('avg_ms')
            
            # ORM performance
            if 'orm_operations' in data and data['orm_operations']:
                orm_times = [stats['avg_ms'] for stats in data['orm_operations'].values() if 'avg_ms' in stats]
                if orm_times:
                    metrics[db_type]['orm_avg'] = statistics.mean(orm_times)
            
            # SQL performance
            if 'raw_sql_operations' in data and data['raw_sql_operations']:
                sql_times = [stats['avg_ms'] for stats in data['raw_sql_operations'].values() if 'avg_ms' in stats]
                if sql_times:
                    metrics[db_type]['sql_avg'] = statistics.mean(sql_times)
            
            # Cold vs warm (Azure SQL specific)
            if 'cold_vs_warm' in data and data['cold_vs_warm']:
                metrics[db_type]['cold_start'] = data['cold_vs_warm'].get('cold_start_ms')
                metrics[db_type]['warm_query'] = data['cold_vs_warm'].get('warm_query_1_ms')
        
        return metrics
    
    def calculate_performance_ratios(self, metrics):
        """Calculate performance ratios between databases"""
        ratios = {}
        
        # Use Docker as baseline (fastest local performance)
        baseline = metrics.get('docker', {})
        
        for db_type, db_metrics in metrics.items():
            if db_type == 'docker':
                continue
                
            ratios[db_type] = {}
            
            for metric_name, value in db_metrics.items():
                baseline_value = baseline.get(metric_name)
                
                if value is not None and baseline_value is not None and baseline_value > 0:
                    ratio = value / baseline_value
                    ratios[db_type][metric_name] = {
                        'ratio': ratio,
                        'difference_ms': value - baseline_value,
                        'slower_by': f"{((ratio - 1) * 100):.1f}%"
                    }
        
        return ratios
    
    def display_comparison_table(self, metrics):
        """Display performance comparison table"""
        print("\n📊 Performance Comparison Table")
        print("=" * 80)
        
        # Table header
        db_types = list(metrics.keys())
        print(f"{'Metric':<20}", end="")
        for db_type in db_types:
            print(f"{db_type.upper():<15}", end="")
        print("Best")
        print("-" * 80)
        
        # Performance metrics
        metric_labels = {
            'connection_avg': 'Connection (ms)',
            'orm_avg': 'ORM Avg (ms)',
            'sql_avg': 'SQL Avg (ms)',
            'cold_start': 'Cold Start (ms)',
            'warm_query': 'Warm Query (ms)'
        }
        
        for metric_key, label in metric_labels.items():
            print(f"{label:<20}", end="")
            
            values = {}
            for db_type in db_types:
                value = metrics[db_type].get(metric_key)
                if value is not None:
                    values[db_type] = value
                    print(f"{value:<15.1f}", end="")
                else:
                    print(f"{'N/A':<15}", end="")
            
            # Find best (lowest) value
            if values:
                best_db = min(values.keys(), key=lambda k: values[k])
                print(f"{best_db.upper()}")
            else:
                print("N/A")
        
        print("-" * 80)
    
    def analyze_latency_sources(self, metrics, ratios):
        """Analyze the sources of latency differences"""
        print("\n🔍 Latency Source Analysis")
        print("=" * 50)
        
        # Compare Fabric vs Azure SQL (both cloud-based)
        if 'fabric' in metrics and 'azure_sql' in metrics:
            fabric_orm = metrics['fabric'].get('orm_avg')
            azure_orm = metrics['azure_sql'].get('orm_avg')
            
            if fabric_orm and azure_orm:
                difference = fabric_orm - azure_orm
                percentage = (difference / azure_orm) * 100
                
                print(f"🌐 Cloud Database Comparison:")
                print(f"   Fabric SQL ORM: {fabric_orm:.1f}ms")
                print(f"   Azure SQL ORM: {azure_orm:.1f}ms")
                print(f"   Difference: {difference:+.1f}ms ({percentage:+.1f}%)")
                
                if abs(percentage) < 10:
                    print("   ✅ Performance is very similar - minimal Fabric overhead")
                elif percentage > 0:
                    print("   ⚠️  Fabric SQL is slower - abstraction layer overhead detected")
                else:
                    print("   🚀 Fabric SQL is faster - optimization benefits detected")
        
        # Compare Docker vs Cloud
        if 'docker' in metrics:
            docker_orm = metrics['docker'].get('orm_avg')
            
            print(f"\n🏠 Local vs Cloud Comparison:")
            print(f"   Docker SQL (Local): {docker_orm:.1f}ms" if docker_orm else "   Docker SQL: N/A")
            
            for cloud_db in ['fabric', 'azure_sql']:
                if cloud_db in metrics:
                    cloud_orm = metrics[cloud_db].get('orm_avg')
                    if docker_orm and cloud_orm:
                        diff = cloud_orm - docker_orm
                        pct = (diff / docker_orm) * 100
                        print(f"   {cloud_db.replace('_', ' ').title()}: {cloud_orm:.1f}ms (+{diff:.1f}ms, +{pct:.1f}%)")
        
        # Cold start analysis (Azure SQL)
        if 'azure_sql' in metrics:
            cold = metrics['azure_sql'].get('cold_start')
            warm = metrics['azure_sql'].get('warm_query')
            
            if cold and warm:
                cold_penalty = cold - warm
                cold_pct = (cold_penalty / warm) * 100
                
                print(f"\n❄️  Azure SQL Serverless Cold Start:")
                print(f"   Cold Start: {cold:.1f}ms")
                print(f"   Warm Query: {warm:.1f}ms")
                print(f"   Cold Penalty: +{cold_penalty:.1f}ms (+{cold_pct:.1f}%)")
                
                if cold_penalty > 100:
                    print("   ⚠️  Significant cold start penalty - consider connection pooling")
                else:
                    print("   ✅ Acceptable cold start impact")
    
    def generate_recommendations(self, metrics, ratios):
        """Generate performance optimization recommendations"""
        print("\n💡 Performance Recommendations")
        print("=" * 50)
        
        # Docker performance (baseline)
        if 'docker' in metrics:
            docker_orm = metrics['docker'].get('orm_avg', 0)
            print(f"🏠 Local Performance Baseline: {docker_orm:.1f}ms")
            
            if docker_orm < 50:
                print("   ✅ Excellent local performance - code is optimized")
            elif docker_orm < 100:
                print("   ✅ Good local performance")
            else:
                print("   ⚠️  Local performance could be improved")
                print("   💡 Consider: Query optimization, indexing, connection pooling")
        
        # Cloud performance recommendations
        cloud_dbs = ['fabric', 'azure_sql']
        worst_cloud_time = 0
        worst_cloud_db = None
        
        for db_type in cloud_dbs:
            if db_type in metrics:
                orm_time = metrics[db_type].get('orm_avg', 0)
                if orm_time > worst_cloud_time:
                    worst_cloud_time = orm_time
                    worst_cloud_db = db_type
        
        if worst_cloud_db and worst_cloud_time > 200:
            print(f"\n🌐 Cloud Performance Issues Detected:")
            print(f"   Worst: {worst_cloud_db.replace('_', ' ').title()} at {worst_cloud_time:.1f}ms")
            print("   💡 Recommendations:")
            print("      • Check network latency to database region")
            print("      • Implement connection pooling")
            print("      • Use database query optimization")
            print("      • Consider caching frequently accessed data")
            print("      • Review database service tier/scaling")
        
        # Specific recommendations by database type
        if 'fabric' in ratios:
            fabric_ratios = ratios['fabric']
            if any(r.get('ratio', 1) > 2 for r in fabric_ratios.values()):
                print(f"\n🔶 Microsoft Fabric Recommendations:")
                print("      • Review Fabric SQL endpoint configuration")
                print("      • Check workspace capacity and scaling")
                print("      • Consider data warehouse optimization")
                print("      • Implement query result caching")
        
        if 'azure_sql' in metrics:
            cold_start = metrics['azure_sql'].get('cold_start')
            warm = metrics['azure_sql'].get('warm_query')
            
            if cold_start and warm and (cold_start > warm * 2):
                print(f"\n🔵 Azure SQL Serverless Recommendations:")
                print("      • Implement application-level connection warming")
                print("      • Consider higher minimum vCore setting")
                print("      • Use connection pooling to maintain warm connections")
                print("      • Evaluate if provisioned compute is more suitable")
    
    def save_comparison_report(self, metrics, ratios):
        """Save detailed comparison report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = {
            'comparison_info': {
                'generated_at': datetime.now().isoformat(),
                'databases_compared': list(metrics.keys())
            },
            'metrics': metrics,
            'performance_ratios': ratios
        }
        
        filename = f"database_comparison_{timestamp}.json"
        filepath = self.results_dir / filename
        
        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Comparison report saved: {filename}")
    
    def run_comparison(self):
        """Run complete performance comparison analysis"""
        print("🔵 Database Performance Comparison Analysis")
        print("=" * 60)
        print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Load and analyze results
        results = self.load_results()
        
        if len(results) < 2:
            print("\n❌ Need at least 2 database results to compare")
            print("💡 Run performance tests on multiple databases first:")
            print("   • Docker: python tests/performance/latency_benchmark.py")
            print("   • Fabric: python tests/performance/fabric_quick_test.py")
            print("   • Azure SQL: python tests/performance/azure_sql_performance_test.py")
            return
        
        metrics = self.extract_key_metrics(results)
        ratios = self.calculate_performance_ratios(metrics)
        
        # Display analysis
        self.display_comparison_table(metrics)
        self.analyze_latency_sources(metrics, ratios)
        self.generate_recommendations(metrics, ratios)
        
        # Save report
        self.save_comparison_report(metrics, ratios)
        
        print(f"\n⏰ Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n🎯 Key Insights:")
        
        # Quick summary insights
        if 'docker' in metrics and 'fabric' in metrics:
            docker_time = metrics['docker'].get('orm_avg', 0)
            fabric_time = metrics['fabric'].get('orm_avg', 0)
            
            if docker_time > 0 and fabric_time > 0:
                factor = fabric_time / docker_time
                print(f"   • Fabric is {factor:.1f}x slower than Docker")
                
                if factor > 5:
                    print("   • Significant network/cloud latency detected")
                elif factor > 2:
                    print("   • Moderate cloud overhead - within expected range")
                else:
                    print("   • Minimal cloud overhead - excellent performance")

def main():
    """Main comparison execution"""
    try:
        comparator = DatabasePerformanceComparator()
        comparator.run_comparison()
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")

if __name__ == "__main__":
    main()
