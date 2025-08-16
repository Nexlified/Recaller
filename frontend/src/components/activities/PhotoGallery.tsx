'use client';

import React, { useState } from 'react';
import { ActivityPhoto } from '../../types/Activity';

interface PhotoGalleryProps {
  photos: ActivityPhoto[];
  onPhotoClick: (photo: ActivityPhoto) => void;
  onPhotoDelete?: (photoId: string) => void;
  className?: string;
}

interface LightboxProps {
  photo: ActivityPhoto;
  photos: ActivityPhoto[];
  onClose: () => void;
  onNext: () => void;
  onPrevious: () => void;
  onDelete?: (photoId: string) => void;
}

const Lightbox: React.FC<LightboxProps> = ({
  photo,
  photos,
  onClose,
  onNext,
  onPrevious,
  onDelete,
}) => {
  const currentIndex = photos.findIndex(p => p.id === photo.id);
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === photos.length - 1;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Escape':
        onClose();
        break;
      case 'ArrowLeft':
        if (!isFirst) onPrevious();
        break;
      case 'ArrowRight':
        if (!isLast) onNext();
        break;
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  return (
    <div 
      className="fixed inset-0 z-50 bg-black bg-opacity-90 flex items-center justify-center"
      onClick={onClose}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <div className="relative max-w-7xl max-h-full mx-4" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 text-white hover:text-gray-300 bg-black bg-opacity-50 rounded-full p-2"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        {/* Previous Button */}
        {!isFirst && (
          <button
            onClick={onPrevious}
            className="absolute left-4 top-1/2 transform -translate-y-1/2 z-10 text-white hover:text-gray-300 bg-black bg-opacity-50 rounded-full p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
        )}

        {/* Next Button */}
        {!isLast && (
          <button
            onClick={onNext}
            className="absolute right-4 top-1/2 transform -translate-y-1/2 z-10 text-white hover:text-gray-300 bg-black bg-opacity-50 rounded-full p-2"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        )}

        {/* Image */}
        <div className="relative">
          <img
            src={photo.url}
            alt={photo.caption || 'Activity photo'}
            className="max-w-full max-h-[80vh] object-contain mx-auto"
          />
        </div>

        {/* Photo Info */}
        <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {photo.caption && (
                <h3 className="text-lg font-medium mb-1">{photo.caption}</h3>
              )}
              <div className="flex items-center space-x-4 text-sm text-gray-300">
                {photo.taken_at && (
                  <span>📅 {formatDate(photo.taken_at)}</span>
                )}
                <span>📷 Photo {currentIndex + 1} of {photos.length}</span>
              </div>
            </div>
            
            {onDelete && (
              <button
                onClick={() => onDelete(photo.id)}
                className="ml-4 text-red-400 hover:text-red-300"
                title="Delete photo"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export const PhotoGallery: React.FC<PhotoGalleryProps> = ({
  photos,
  onPhotoClick,
  onPhotoDelete,
  className = '',
}) => {
  const [lightboxPhoto, setLightboxPhoto] = useState<ActivityPhoto | null>(null);

  const openLightbox = (photo: ActivityPhoto) => {
    setLightboxPhoto(photo);
    onPhotoClick(photo);
  };

  const closeLightbox = () => {
    setLightboxPhoto(null);
  };

  const goToNext = () => {
    if (!lightboxPhoto) return;
    const currentIndex = photos.findIndex(p => p.id === lightboxPhoto.id);
    const nextIndex = (currentIndex + 1) % photos.length;
    const nextPhoto = photos[nextIndex];
    setLightboxPhoto(nextPhoto);
    onPhotoClick(nextPhoto);
  };

  const goToPrevious = () => {
    if (!lightboxPhoto) return;
    const currentIndex = photos.findIndex(p => p.id === lightboxPhoto.id);
    const prevIndex = currentIndex === 0 ? photos.length - 1 : currentIndex - 1;
    const prevPhoto = photos[prevIndex];
    setLightboxPhoto(prevPhoto);
    onPhotoClick(prevPhoto);
  };

  const handleDelete = (photoId: string) => {
    if (onPhotoDelete && window.confirm('Are you sure you want to delete this photo?')) {
      onPhotoDelete(photoId);
      // Close lightbox if the deleted photo was open
      if (lightboxPhoto?.id === photoId) {
        closeLightbox();
      }
    }
  };

  if (photos.length === 0) {
    return (
      <div className={`text-center py-8 ${className}`}>
        <div className="text-gray-400 dark:text-gray-500 mb-3">
          <svg className="mx-auto h-8 w-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          No photos in this activity yet
        </p>
      </div>
    );
  }

  return (
    <>
      <div className={`${className}`}>
        {/* Grid Layout */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {photos.map((photo, index) => (
            <div
              key={photo.id}
              className="group relative aspect-square bg-gray-100 dark:bg-gray-700 rounded-lg overflow-hidden cursor-pointer"
              onClick={() => openLightbox(photo)}
            >
              <img
                src={photo.thumbnail_url || photo.url}
                alt={photo.caption || `Photo ${index + 1}`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform"
              />
              
              {/* Overlay */}
              <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-30 transition-opacity flex items-center justify-center">
                <svg className="w-8 h-8 text-white opacity-0 group-hover:opacity-100 transition-opacity" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>

              {/* Caption Overlay */}
              {photo.caption && (
                <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white p-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
                  <p className="truncate">{photo.caption}</p>
                </div>
              )}

              {/* Delete Button */}
              {onPhotoDelete && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(photo.id);
                  }}
                  className="absolute top-2 right-2 text-white bg-red-600 hover:bg-red-700 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Delete photo"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                )}
            </div>
          ))}
        </div>

        {/* Photo Count */}
        {photos.length > 0 && (
          <div className="mt-4 text-center text-sm text-gray-500 dark:text-gray-400">
            {photos.length} photo{photos.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>

      {/* Lightbox */}
      {lightboxPhoto && (
        <Lightbox
          photo={lightboxPhoto}
          photos={photos}
          onClose={closeLightbox}
          onNext={goToNext}
          onPrevious={goToPrevious}
          onDelete={onPhotoDelete ? handleDelete : undefined}
        />
      )}
    </>
  );
};