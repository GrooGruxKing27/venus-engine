## Venus Engine v0 — Input / Output Contract

### Inputs (v0)
- Cropped image of a single clothing item
- No user-specific data required
- Accepted formats: (jpg/png)
- Assumption: image is already cropped to clothing

### Outputs
- Dominant color palette (RGB + %)
- Representative fabric color
- Friendly color label (e.g., "Blue")
- Anchor named color (e.g., "Steel Blue")
- Optional confidence score (future)

### Explicit Non-Goals (v0)
- No user profile input (skin tone, body shape, etc.)
- No personalization logic
- No person detection
- No skin tone or body analysis
- No automatic cropping
- No pattern or texture detection (yet)

### Notes
- Engine must be deterministic
- Engine must work without user profile data

### Future Considerations
- Engine may accept optional user profile data to adjust scoring,
  but must always function without it.