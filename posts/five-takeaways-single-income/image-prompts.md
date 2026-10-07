# Intro image prompts: The Single Income Stress Test: five takeaways

Two images for the intro: a peaceful close view of a woman on a forest trail,
then the same scene shown wider, with a man aiming a rifle at her from the right.

The two must be the same picture. An image tool will not draw the same woman
and the same forest twice. So generate ONE wide image, and the first image is
cut from its left side. Claude does the cut once the wide image is in
`images/` as `00b-forest-wide.jpg`; the cut is saved as `00a-forest-close.jpg`.

## Prompt A: the wide image (generate this one)

Photorealistic wide landscape photograph, 16:9, of a hiking trail through a beautiful, sunlit forest in early morning. In the left third of the frame, in sharp focus, a woman in her thirties in ordinary hiking clothes and a small daypack stands on the trail, seen from the waist up, facing the camera. Her eyes are closed and her face is tilted slightly up into a shaft of warm sunlight. She looks completely at peace, simply taking in the place. Golden light filters down through tall trees and catches the mist and the ferns around her. The center of the frame is open forest. In the right third of the frame, about thirty yards behind her and partly screened by tree trunks but clearly visible, a man in dull green hunting clothes stands braced against a tree with a hunting rifle raised to his shoulder, aimed directly at the woman. She is unaware of him. Natural color, shallow depth of field on the woman, the man slightly softer but unmistakable. No blood, no violence shown, no text, no logos. Keep the man entirely inside the right third so the left half of the image can be cropped to show the woman alone.

## Prompt B: if the tool refuses Prompt A

Same as Prompt A, but replace the sentence about the man with: "In the right third of the frame, about thirty yards behind her and partly screened by tree trunks but clearly visible, a hunter in dull green clothes stands braced against a tree with a rifle raised to his shoulder, pointed in the direction of the trail where she stands."

## Prompt C: only if Eric wants the first image generated on its own

Photorealistic portrait photograph, 4:5, of a woman in her thirties in ordinary hiking clothes and a small daypack standing on a hiking trail in a beautiful, sunlit forest in early morning, seen from the waist up, facing the camera. Her eyes are closed and her face is tilted slightly up into a shaft of warm sunlight. She looks completely at peace. Golden light filters down through tall trees and catches the mist and the ferns around her. Natural color, shallow depth of field. No other people, no text, no logos.

Note: with Prompt C the second image will not match the first. The woman, her clothes and the trees will differ.
