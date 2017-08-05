# HTML5 spec table parsing function
# In html table, the number of elements varies 
# by colspan & rowspan.
# pandas.read_html does not handle this, for example.

class Cell(object):
	def __init__(self, x, y, col, row, e):
		self.x = x
		self.y = y
		self.colspan = col
		self.rowspan = row
		self.element = e

class Table(object):
	def __init__(self, et, quirks=False):
		self.quirks = quirks
		self.xw = self.yh = 0
		self.x = self.y = 0
		self.coords = {}
		self.tfoot = []
		
		step_to_row = False
		for c in et.getchildren():
			if not step_to_row:
				if c.tag not in ("colgroup","thead", "tbody","tfoot","tr"):
					continue
				
				if c.tag == "colgroup":
					continue
				
				self.y = 0
				self.downs = []
			
			# Row
			if c.tag not in ("thead","tbody","tfoot","tr"):
				continue
			
			if c.tag == "tr":
				self.proc_row(c)
				step_to_row = True
				continue
			
			self.end_row_group(c)
			
			if c.tag == "tfoot":
				self.tfoot.append(c)
				continue
			
			assert c.tag in ("thead","tbody")
			self.row_groups(c)
		
		# End
		for tfoot in self.tfoot:
			self.row_groups(tfoot)
		
		# slot check
		self.matrix()
	
	def matrix(self, conv=None):
		rows = []
		for y in range(self.yh):
			row = []
			for x in range(self.xw):
				k = (x,y)
				els = self.coords.get(k, [])
				assert len(els) == 1
				if conv is None:
					row.append(els[0].element)
				else:
					row.append(conv(els[0].element))
			rows.append(row)
		return rows
	
	def row_groups(self, c):
		y = self.yh
		for t in c.getchildren():
			if t.tag == "tr":
				self.proc_row(t)
		if self.yh > y:
			# form RowGroup
			pass
		
		self.end_row_group(c)
	
	def end_row_group(self, c):
		if self.y < self.yh:
			self.grow_downs()
			self.y += 1
		self.downs = []
	
	def proc_row(self, c):
		assert c.tag == "tr"
		
		if self.yh == self.y:
			self.yh += 1
		self.x = 0
		self.grow_downs()
		if not [d for d in c.getchildren() if d.tag in ("td","th")]:
			self.y += 1
			return
		
		cells = [d for d in c.getchildren() if d.tag in ("td","th")]
		for cc in cells:
			if self.x < self.xw and self.coords.get((self.x, self.y)):
				self.x += 1
			
			if self.x==self.xw:
				self.xw += 1
			
			try:
				colspan = int(cc.get("colspan"))
				assert colspan != 0
			except:
				colspan = 1
			
			try:
				rowspan = int(cc.get("rowspan"))
			except:
				rowspan = 1
			
			if rowspan==0 and not self.quirks:
				grows_downward= True
				rowspan = 1
			else:
				grows_downward= False
			
			if self.xw < self.x + colspan:
				self.xw = self.x + colspan
			
			if self.yh < self.y + rowspan:
				self.yh = self.y + rowspan
			
			cell = Cell(self.x, self.y, colspan, rowspan, cc)
			for x in range(self.x, self.x+colspan):
				for y in range(self.y, self.y+rowspan):
					k = (x,y)
					if k in self.coords:
						# table error
						self.coords[k].append(cell)
					else:
						self.coords[k] = [cell]
			
			# assigning header cells
			
			if grows_downward:
				self.downs.append((cell, self.x, colspan))
			
			self.x += colspan
		
		self.y += 1
	
	def grow_downs(self):
		for cell, cellx, width in self.downs:
			for x in range(self.x, self.x+width):
				k = (x, self.y)
				v = self.coords.get(k, [])
				if cell not in v:
					v.append(cell)
				self.coords[k] = v
