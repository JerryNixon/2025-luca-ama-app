"""
Django Management Command: Generate Embeddings for Questions

This command generates vector embeddings for all questions in the database
using Azure OpenAI's text-embedding-ada-002 model. It's designed to populate
embeddings for existing questions or refresh embeddings after model changes.

Usage:
    python manage.py generate_embeddings
    python manage.py generate_embeddings --batch-size 10
    python manage.py generate_embeddings --dry-run
    python manage.py generate_embeddings --force-refresh
"""

import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from api.models import Question
from api.fabric_ai_service import FabricAIService

# Set up logging for this command
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Generate vector embeddings for questions using Azure OpenAI'
    
    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of questions to process at once (default: 10)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes'
        )
        
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Regenerate embeddings for questions that already have them'
        )
        
        parser.add_argument(
            '--event-id',
            type=str,
            help='Only process questions from a specific event (UUID)'
        )
    
    def handle(self, *args, **options):
        """Main command execution"""
        try:
            # Initialize the AI service
            self.stdout.write("🤖 Initializing Fabric AI Service...")
            ai_service = FabricAIService()
            
            # Get command options
            batch_size = options['batch_size']
            dry_run = options['dry_run']
            force_refresh = options['force_refresh']
            event_id = options.get('event_id')
            
            # Build query for questions to process
            query = Question.objects.all()
            
            # Filter by event if specified
            if event_id:
                query = query.filter(event__id=event_id)
                self.stdout.write(f"📍 Filtering to event: {event_id}")
            
            # Filter by embedding status unless force refresh
            if not force_refresh:
                query = query.filter(
                    fabric_ai_processed=False
                ).filter(
                    embedding_vector__isnull=True
                )
                self.stdout.write("📋 Processing only questions without embeddings")
            else:
                self.stdout.write("🔄 Force refresh: processing ALL questions")
            
            # Get questions to process
            questions = list(query.order_by('created_at'))
            total_count = len(questions)
            
            if total_count == 0:
                self.stdout.write(
                    self.style.WARNING("✅ No questions need embedding generation!")
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS(f"📊 Found {total_count} questions to process")
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING("🔍 DRY RUN - No changes will be made")
                )
                for i, question in enumerate(questions[:5], 1):
                    self.stdout.write(f"  {i}. {question.text[:60]}...")
                if total_count > 5:
                    self.stdout.write(f"  ... and {total_count - 5} more questions")
                return
            
            # Process questions in batches
            success_count = 0
            error_count = 0
            
            for i in range(0, total_count, batch_size):
                batch = questions[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total_count + batch_size - 1) // batch_size
                
                self.stdout.write(
                    f"\n🔄 Processing batch {batch_num}/{total_batches} "
                    f"({len(batch)} questions)..."
                )
                
                batch_success = 0
                batch_errors = 0
                
                for question in batch:
                    try:
                        # Generate embedding for this question
                        self.stdout.write(f"  📝 Processing: {question.text[:50]}...")
                        
                        # Mark processing start time
                        question.ai_processing_started_at = timezone.now()
                        question.save(update_fields=['ai_processing_started_at'])
                        
                        # Generate embedding using Fabric AI service
                        embedding_binary, embedding_json = ai_service.generate_embedding_with_fabric(
                            question.text
                        )
                        
                        if embedding_binary:
                            # Update question with embedding data
                            with transaction.atomic():
                                question.embedding_vector = embedding_binary
                                question.embedding_json = str(embedding_json) if embedding_json else None
                                question.fabric_ai_processed = True
                                question.fabric_similarity_indexed = True
                                question.ai_processing_completed_at = timezone.now()
                                question.ai_processing_error = None
                                question.save()
                            
                            self.stdout.write(f"    ✅ Generated embedding ({len(embedding_binary)} bytes)")
                            batch_success += 1
                            
                        else:
                            # Handle embedding generation failure
                            question.ai_processing_error = "Failed to generate embedding"
                            question.ai_processing_completed_at = timezone.now()
                            question.save(update_fields=[
                                'ai_processing_error', 
                                'ai_processing_completed_at'
                            ])
                            
                            self.stdout.write(f"    ❌ Failed to generate embedding")
                            batch_errors += 1
                    
                    except Exception as e:
                        # Handle unexpected errors
                        error_msg = f"Unexpected error: {str(e)}"
                        logger.error(f"Error processing question {question.id}: {e}")
                        
                        try:
                            question.ai_processing_error = error_msg
                            question.ai_processing_completed_at = timezone.now()
                            question.save(update_fields=[
                                'ai_processing_error',
                                'ai_processing_completed_at'
                            ])
                        except Exception as save_error:
                            logger.error(f"Failed to save error state: {save_error}")
                        
                        self.stdout.write(f"    ❌ Error: {error_msg}")
                        batch_errors += 1
                
                # Batch summary
                success_count += batch_success
                error_count += batch_errors
                
                self.stdout.write(
                    f"  📊 Batch {batch_num} complete: "
                    f"{batch_success} success, {batch_errors} errors"
                )
            
            # Final summary
            self.stdout.write(f"\n🎉 Embedding generation complete!")
            self.stdout.write(f"  ✅ Successfully processed: {success_count}")
            self.stdout.write(f"  ❌ Errors encountered: {error_count}")
            self.stdout.write(f"  📊 Total questions: {total_count}")
            
            if success_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\n🚀 {success_count} questions now have embeddings for similarity detection!"
                    )
                )
            
            if error_count > 0:
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️  {error_count} questions had errors. Check logs for details."
                    )
                )
        
        except Exception as e:
            logger.error(f"Command failed: {e}")
            raise CommandError(f"Failed to generate embeddings: {e}")
