import { useState, useEffect, useRef } from 'react';
import { cn } from '@/lib/utils';
import { OptimizedImageProps, getOptimizedImageUrl, lazyLoadImage } from '@/lib/imageOptimization';

/**
 * Optimized Image Component with lazy loading and responsive images
 */
export default function OptimizedImage({
  src,
  alt,
  width,
  height,
  className,
  loading = 'lazy',
  quality = 75,
  sizes,
}: OptimizedImageProps) {
  const imgRef = useRef<HTMLImageElement>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);

  const optimizedSrc = getOptimizedImageUrl({ src, width, quality });

  useEffect(() => {
    const img = imgRef.current;
    if (!img || loading !== 'lazy') return;

    lazyLoadImage(img);
  }, [loading]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setError(true);
  };

  if (error) {
    return (
      <div
        className={cn(
          'flex items-center justify-center bg-muted text-muted-foreground',
          className
        )}
        style={{ width, height }}
      >
        <span className="text-sm">Failed to load image</span>
      </div>
    );
  }

  return (
    <div className={cn('relative overflow-hidden', className)} style={{ width, height }}>
      {/* Placeholder blur */}
      {!isLoaded && (
        <div className="absolute inset-0 bg-muted animate-pulse" />
      )}
      
      <img
        ref={imgRef}
        src={loading === 'eager' ? optimizedSrc : undefined}
        data-src={loading === 'lazy' ? optimizedSrc : undefined}
        alt={alt}
        width={width}
        height={height}
        sizes={sizes}
        loading={loading}
        onLoad={handleLoad}
        onError={handleError}
        className={cn(
          'transition-opacity duration-300',
          isLoaded ? 'opacity-100' : 'opacity-0',
          className
        )}
      />
    </div>
  );
}
