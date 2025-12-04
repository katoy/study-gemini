package com.example;

import processing.core.PApplet;
import processing.core.PFont;

public class Button {
  PApplet p;
  String label;
  float x, y, w, h;
  int strokeColor;
  PFont japaneseFont;

  // Constructor with default black stroke
  public Button(PApplet p, String label, float x, float y, float w, float h, PFont font) {
    this(p, label, x, y, w, h, p.color(0), font); // Delegate to the other constructor
  }
  
  // Constructor with custom stroke color
  public Button(PApplet p, String label, float x, float y, float w, float h, int strokeCol, PFont font) {
    this.p = p;
    this.label = label;
    this.x = x; this.y = y; this.w = w; this.h = h;
    this.strokeColor = strokeCol;
    this.japaneseFont = font;
  }
  
  public void draw() {
    p.stroke(this.strokeColor); // Use the stroke color
    p.strokeWeight(1); // Keep a consistent stroke weight
    p.fill(200);
    p.rect(x, y, w, h);
    
    // Reset stroke to default for other elements
    p.stroke(0); 
    p.strokeWeight(1);

    p.fill(0);
    p.textAlign(PApplet.CENTER, PApplet.CENTER);
    p.textFont(japaneseFont, 16); // フォント適用
    p.text(label, x + w/2, y + h/2);
  }
  
  public boolean isClicked() {
    return p.mousePressed && p.mouseX > x && p.mouseX < x + w && p.mouseY > y && p.mouseY < y + h;
  }
}
