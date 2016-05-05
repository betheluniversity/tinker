'use strict';

// requirements

var gulp = require('gulp'),
    browserify = require('gulp-browserify'),
    size = require('gulp-size'),
    clean = require('gulp-clean');

var scripts =  [
                './tinker/static/scripts/jsx/*.js',
                './tinker/**/static/scripts/jsx/*.js',
                './tinker/**/**/scripts/*.js'
              ];

gulp.task('transform', function () {
  return gulp.src(scripts)
    .pipe(browserify({transform: ['reactify']}))
    .pipe(gulp.dest('./tinker/static/scripts/js'))
    .pipe(size());
});

gulp.task('clean', function () {
  return gulp.src(['./tinker/static/scripts/js'], {read: false})
    .pipe(clean());
});

gulp.task('default', ['clean'], function() {
  gulp.start('transform');
  gulp.watch(scripts, ['transform']);
});