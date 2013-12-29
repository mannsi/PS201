#ifndef DEF_H
#define DEF_H

// For readability
#define BIT(x) 						(0x01 << (x))
#define BIT_SET(x,y) 				((x) |= (y))
#define BIT_CLEAR(x,y)	 			((x) &= (~(y)))
#define BIT_FLIP(x,y)				((x) ^= (y))
#define BIT_GET(x,y)	 			((x) & (y))
#define BIT_VAL(x,y) 				(((x)>>(y)) & 1)

#endif
